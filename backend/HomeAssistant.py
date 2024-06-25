import json
from threading import Thread, Semaphore
from time import sleep
from typing import Dict, Callable, Any, List

from loguru import logger as log
from plugins.de_gensyn_HomeAssistantPlugin.backend.const import CONNECTED, CONNECTING, DISCONNECTING, NOT_CONNECTED, \
    AUTHENTICATING, WAITING_FOR_RETRY
from websocket import create_connection, WebSocket

HASS_WEBSOCKET_API = "/api/websocket?latest"

FIELD_EVENT = "event"

ENTITY_ID = "entity_id"
ID = "id"

FIELD_TYPE = "type"
FIELD_SUCCESS = "success"
FIELD_RESULT = "result"

BUTTON_ENCODE_SYMBOL = "-"

RECV_LOOP_TIMEOUT = 300

BUTTON_ENTITIES: Dict[str, str] = {}

WEBSOCKET_SEMAPHORE = Semaphore(1)
ENTITIES_UPDATE_SEMAPHORE = Semaphore(1)

PING_INTERVAL = 30

RETRY_CONNECTION = False


class HomeAssistantBackend:
    _websocket: WebSocket = None
    _changes_websocket: WebSocket = None
    _message_id: int = 0
    _domains: list = []
    _entities: dict = {}
    _services: dict = {}
    _host: str = ""
    _port: str = ""
    _ssl: bool = True
    _token: str = ""
    _connection_status_callback: Callable = lambda _1, _2: None
    _keep_alive_thread: Thread = None
    _reconnect_thread: Thread = None
    _action_list: List[Callable] = []

    def __init__(self):
        super().__init__()

    def set_host(self, host: str) -> None:
        if "//" in host:
            host = host.split("//")[1]

        if self._host == host:
            return

        self._host = host
        self.reconnect()

    def set_port(self, port: str) -> None:
        if self._port == port:
            return

        self._port = port
        self.reconnect()

    def set_ssl(self, ssl: bool) -> None:
        if self._ssl == ssl:
            return

        self._ssl = ssl
        self.reconnect()

    def set_token(self, token: str) -> None:
        if self._token == token:
            return

        self._token = token
        self.reconnect()

    def set_connection_status_callback(self, callback: Callable) -> None:
        self._connection_status_callback = callback

    def reconnect(self) -> bool:
        self.disconnect()
        success = self.connect()

        if not success and self._host and self._token and self._port:
            if not self._reconnect_thread or not self._reconnect_thread.is_alive():
                self._reconnect_thread = Thread(target=self.retry_connect, daemon=True)
                self._reconnect_thread.start()
            else:
                global RETRY_CONNECTION
                RETRY_CONNECTION = True

        return success

    def connect(self) -> bool:
        if self.is_connected():
            # already connected
            return True

        self._connection_status_callback(CONNECTING)

        if not self._host or not self._token or not self._port:
            self._connection_status_callback(NOT_CONNECTED)
            return False

        if self._websocket and self._websocket.connected:
            # close existing websocket
            self._websocket.close()

        if self._changes_websocket and self._changes_websocket.connected:
            # close existing websocket
            self._changes_websocket.close()

        self._connection_status_callback(AUTHENTICATING)

        self._websocket = self._auth()

        if not self._websocket:
            self._connection_status_callback(NOT_CONNECTED)
            return False

        self._changes_websocket = self._auth()

        if not self._changes_websocket:
            self._websocket.close()
            self._connection_status_callback(NOT_CONNECTED)
            return False

        message = self.create_message("get_config")
        config = self._send_and_wait_for_response(message)

        result: Dict[str, dict] = _get_field_from_message(config, FIELD_RESULT)

        if not result or result.get("state", "") != "RUNNING":
            # Home Assistant hasn't finished starting yet so not all entities
            # might have been initialized - try again later
            self._websocket.close()
            self._changes_websocket.close()
            self._connection_status_callback(NOT_CONNECTED)
            return False

        log.info("Connected to Home Assistant")
        self._connection_status_callback(CONNECTED)

        Thread(target=self._async_run_recv_loop, daemon=True).start()

        if not self._keep_alive_thread or not self._keep_alive_thread.is_alive():
            self._keep_alive_thread = Thread(target=self._keep_alive, daemon=True)
            self._keep_alive_thread.start()

        ENTITIES_UPDATE_SEMAPHORE.acquire()
        self._load_domains_and_entities()
        ENTITIES_UPDATE_SEMAPHORE.release()

        # tell actions that we are connected
        for action in self._action_list:
            action()

        return True

    def disconnect(self) -> None:
        self._connection_status_callback(DISCONNECTING)

        global RETRY_CONNECTION
        RETRY_CONNECTION = False

        if self._websocket and self._websocket.connected:
            self._websocket.close()

        if self._changes_websocket and self._changes_websocket.connected:
            self._changes_websocket.close()

        self._connection_status_callback(NOT_CONNECTED)

    def _auth(self):
        websocket_host = f'{"wss://" if self._ssl else "ws://"}{self._host}:{self._port}{HASS_WEBSOCKET_API}'

        try:
            new_websocket = create_connection(websocket_host)

            auth_required = new_websocket.recv()
            auth_required = _get_field_from_message(auth_required, FIELD_TYPE)

            if not auth_required:
                log.error("Could not auth with Home Assistant")
                return None

            new_websocket.send(json.dumps({FIELD_TYPE: "auth", "access_token": self._token}))

            auth_ok = new_websocket.recv()
            auth_ok = _get_field_from_message(auth_ok, FIELD_TYPE)

            if not auth_ok or "auth_ok" != auth_ok:
                log.error("Could not auth with Home Assistant")
                return None
        except ConnectionRefusedError:
            log.error(
                f'Connection refused by {websocket_host}. Make sure'
                f" 'websocket_api' is enabled in your Home Assistant configuration."
            )
            return None
        except Exception as e:
            log.error(
                f"Could not connect to {websocket_host}: {e}"
            )
            return None

        return new_websocket

    def _async_run_recv_loop(self):
        # wait for entities update finishing
        ENTITIES_UPDATE_SEMAPHORE.acquire()
        ENTITIES_UPDATE_SEMAPHORE.release()

        if self._entities:
            # if the collection was lost we might need to resubscribe to entity events
            for domain in self._entities.keys():
                for entity, entity_settings in self._entities[domain].items():
                    if entity_settings.get("keys"):
                        action_items = entity_settings["keys"].items()

                        entity_settings["subscription_id"] = -1
                        entity_settings["keys"] = {}

                        for action_uid, action in action_items:
                            self.add_tracked_entity(entity, action_uid, action)

        while self._changes_websocket.connected:
            try:
                message = self._changes_websocket.recv()
            except Exception as e:
                log.info(f"Connection closed; quitting recv() loop: {e}")
                break

            if not message:
                # received an empty message - happens when Home Assistants shuts down; ignore
                continue

            message_type = _get_field_from_message(message, FIELD_TYPE)

            if FIELD_EVENT == message_type:
                new_state = (
                    json.loads(message).get(FIELD_EVENT, {}).get("variables", {}).get("trigger", {}).get("to_state", {})
                )

                entity_id = new_state.get(ENTITY_ID)

                domain = entity_id.split(".")[0]

                entity_settings = self._entities[domain].get(entity_id)

                actions = entity_settings.get("keys").values()

                state = new_state.get("state")

                attributes = new_state.get("attributes", {})

                self._entities[domain][entity_id]["state"] = state
                self._entities[domain][entity_id]["attributes"] = attributes

                update_state = {
                    "state": state,
                    "attributes": attributes,
                }

                for action_entity_updated in actions:
                    try:
                        action_entity_updated(entity_id, update_state)
                    except Exception as e:
                        log.exception(f"Ex: {e}")

        self._websocket.close()
        self._connection_status_callback(NOT_CONNECTED)

        if not self._reconnect_thread or not self._reconnect_thread.is_alive():
            self._reconnect_thread = Thread(target=self.retry_connect, daemon=True)
            self._reconnect_thread.start()
        else:
            global RETRY_CONNECTION
            RETRY_CONNECTION = True

    def get_state(self, entity_id: str) -> str:
        if not self.connect() or "." not in entity_id:
            return "off"

        self._load_domains_and_entities()

        domain = entity_id.split(".")[0]

        return self._entities[domain][entity_id]["state"]

    def get_domains(self) -> list:
        if not self.connect():
            return []

        if not self._domains:
            self._load_domains_and_entities()

        return self._domains

    def get_entity(self, entity_id: str) -> dict:
        if not entity_id or "." not in entity_id:
            return {}

        domain = entity_id.split(".")[0]
        return self._entities.get(domain, {}).get(entity_id, {})

    def get_entities(self, domain: str) -> list:
        if not self.connect() or not domain:
            return []

        if not self._entities:
            self._load_domains_and_entities()

        return list(self._entities.get(domain, {}).keys())

    def _load_domains_and_entities(self) -> None:
        message = self.create_message("get_states")

        response = self._send_and_wait_for_response(message)

        success = _get_field_from_message(response, FIELD_SUCCESS)

        domains = []
        entities = {}

        if not success:
            log.error("Error retrieving domains and entities.")
            return

        for entity in _get_field_from_message(response, "result"):
            entity_id = entity.get(ENTITY_ID)

            domain = entity_id.split(".")[0]

            if domain not in domains:
                domains.append(domain)

            if domain not in entities:
                entities[domain] = {}

            entities[domain][entity_id] = {
                "state": entity.get("state", "off"),
                "attributes": entity.get("attributes", {}),
                "keys": {},
                "subscription_id": -1,
            }

        if self._entities:
            # entities were already loaded; keep keys and subscription ids
            for domain in self._entities.keys():
                for entity_id, entity_settings in self._entities[domain].items():
                    if entities.get(domain, {}).get(entity_id):
                        entities[domain][entity_id]["keys"] = self._entities[domain][entity_id].get("keys", {})
                        entities[domain][entity_id]["subscription_id"] = self._entities[domain][entity_id].get(
                            "subscription_id", -1)

        self._domains = domains
        self._entities = entities

    def get_services(self, domain: str) -> Dict[str, dict]:
        if not self.connect() or not domain:
            return {}

        if self._services:
            return self._services.get(domain, {})

        message = self.create_message("get_services")

        response = self._send_and_wait_for_response(message)

        success = _get_field_from_message(response, FIELD_SUCCESS)

        self._services = {}

        if not success:
            log.error("Error retrieving services.")
            return {}

        self._services = _get_field_from_message(response, FIELD_RESULT)

        return self._services.get(domain, {})

    def call_service(self, entity_id: str, service: str, data: Dict[str, Any] = {}) -> None:
        if not self.connect():
            return

        domain = entity_id.split(".")[0]

        message = self.create_message("call_service")
        message["domain"] = domain
        message["service"] = service
        message["target"] = {ENTITY_ID: entity_id}
        message["service_data"] = data

        response = self._send_and_wait_for_response(message)

        success = _get_field_from_message(response, FIELD_SUCCESS)

        if not success:
            log.error(f"Error calling service {service} for entity {entity_id}.")

    def create_message(self, message_type: str) -> Dict[str, Any]:
        self._message_id += 1
        return {ID: self._message_id, FIELD_TYPE: message_type}

    def add_tracked_entity(self, entity_id: str, action_uid: str, action_entity_updated: Callable) -> None:
        if not entity_id or not self.connect():
            return

        domain = entity_id.split(".")[0]

        if not self._entities:
            self._load_domains_and_entities()

        entity_settings = self._entities[domain].get(entity_id)

        if not entity_settings:
            # entity doesn't exist (anymore)
            return

        if action_uid in entity_settings.get("keys").keys():
            # key already registered
            return

        entity_settings.get("keys")[action_uid] = action_entity_updated

        if entity_settings.get("subscription_id") > -1:
            # already subscribed to entity events
            return

        message = self.create_message("subscribe_trigger")
        message["trigger"] = {"platform": "state", ENTITY_ID: entity_id}

        message_id = message.get(ID)

        self._changes_websocket.send(json.dumps(message))

        entity_settings["subscription_id"] = message_id

    def remove_tracked_entity(self, entity_id: str, action_uid: str) -> None:
        if not entity_id or not self.connect():
            return

        domain = entity_id.split(".")[0]

        entity_settings = self._entities[domain].get(entity_id)
        entity_settings.get("keys").pop(action_uid, None)

        if len(entity_settings.get("keys")) > 0:
            # the entity is still attached to another key, so keep the trigger subscription
            return

        message = self.create_message("unsubscribe_events")
        message["subscription_id"] = entity_settings["subscription_id"]

        self._changes_websocket.send(json.dumps(message))

        entity_settings["subscription_id"] = -1

    def is_connected(self) -> bool:
        return self._websocket and self._websocket.connected

    def _send_and_wait_for_response(self, message: Dict[str, str | int]) -> str:
        WEBSOCKET_SEMAPHORE.acquire()

        self._websocket.send(json.dumps(message))

        response = self._websocket.recv()

        WEBSOCKET_SEMAPHORE.release()

        return response

    def _keep_alive(self):
        while True:
            sleep(PING_INTERVAL)
            try:
                self._websocket.ping()
            except Exception as e:
                self._connection_status_callback(NOT_CONNECTED)
                return

    def retry_connect(self):
        sleep(10)

        count = 1

        while not self.connect() and count < 3600 and RETRY_CONNECTION:
            self._connection_status_callback(WAITING_FOR_RETRY)
            if count < 13:
                sleep(10)
            else:
                sleep(60)

            count += 1

    def register_action(self, action: Callable):
        if action not in self._action_list:
            self._action_list.append(action)

    def remove_action(self, action: Callable):
        if action in self._action_list:
            self._action_list.remove(action)


def _get_field_from_message(message: str, field: str) -> Any:
    if not message:
        return ""

    try:
        parsed = json.loads(message)

        return parsed.get(field, "")
    except json.JSONDecodeError:
        log.error(f"Could not parse {message}")
        return ""
