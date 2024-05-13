import json
import os
from threading import Thread, Semaphore
from time import sleep
from typing import Dict, Callable, Any, List

from loguru import logger as log
from websocket import create_connection, WebSocket

HASS_WEBSOCKET_API = "/api/websocket?latest"

FIELD_EVENT = "event"

MDI_SVG_JSON = "mdi-svg.json"
ENTITY_ID = "entity_id"
ID = "id"

FIELD_TYPE = "type"
FIELD_SUCCESS = "success"
FIELD_RESULT = "result"

ICON_SCALE = 0.66

COLOR_ON = "#eeff1b"
COLOR_OFF = "#bebebe"

MDI_TRANSFORM = 'fill="<color>" transform="translate(4.5, 5) scale(<scale>)"'

MDI_DEFAULT_PATH = "M7,2V13H10V22L17,10H13L17,2H7Z"

BUTTON_ENCODE_SYMBOL = "-"

RECV_LOOP_TIMEOUT = 300

BUTTON_ENTITIES: Dict[str, str] = {}

CONNECTED = "connected"
NOT_CONNECTED = "not connected"

WEBSOCKET_SEMAPHORE = Semaphore(1)
ENTITIES_UPDATE_SEMAPHORE = Semaphore(1)

PING_INTERVAL = 30

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
    _connection_state = NOT_CONNECTED

    def __init__(self):
        super().__init__()

        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", MDI_SVG_JSON)
        self._mdi_icons = json.loads(open(filename, "r").read())

    def set_host(self, host: str):
        if "//" in host:
            self._host = host.split("//")[1]
        else:
            self._host = host

        self.reconnect()

    def set_port(self, port: str):
        self._port = port
        self.reconnect()

    def set_ssl(self, ssl: bool):
        self._ssl = ssl
        self.reconnect()

    def set_token(self, token: str):
        self._token = token
        self.reconnect()

    def reconnect(self) -> bool:
        self.disconnect()
        return self.connect()

    def connect(self) -> bool:
        if self.is_connected():
            # already connected
            return True

        if not self._host or not self._token or not self._port:
            return False

        if self._websocket and self._websocket.connected:
            # close existing websocket
            self._websocket.close()

        if self._changes_websocket and self._changes_websocket.connected:
            # close existing websocket
            self._changes_websocket.close()

        self._websocket = self._auth()

        if not self._websocket:
            return False

        self._changes_websocket = self._auth()

        if not self._changes_websocket:
            return False

        log.info("Connected to Home Assistant")
        self._connection_state = CONNECTED

        recv_thread = Thread(target=self._async_run_recv_loop, daemon=True)
        recv_thread.start()

        keep_alive_thread = Thread(target=self._keep_alive, daemon=True)
        keep_alive_thread.start()

        ENTITIES_UPDATE_SEMAPHORE.acquire()
        self._load_domains_and_entities()
        ENTITIES_UPDATE_SEMAPHORE.release()

        return True

    def disconnect(self) -> None:
        if self._websocket and self._websocket.connected:
            self._websocket.close()

        if self._changes_websocket and self._changes_websocket.connected:
            self._changes_websocket.close()

        self._connection_state = NOT_CONNECTED

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

                icon = self.get_icon(entity_id, state=state)

                for action_entity_updated in actions:
                    action_entity_updated(entity_id, icon)

        self._websocket.close()
        self._connection_state = NOT_CONNECTED

    def get_icon(self, entity_id: str, service: str = "", state: str = "") -> str:
        if not self.connect():
            return ""

        if not entity_id:
            return ""

        if not self._domains:
            self._load_domains_and_entities()

        domain = entity_id.split(".")[0]

        if "media_player" == domain:
            # use icons for service instead of entity
            if "media_play_pause" == service:
                if not state:
                    state = self.get_state(entity_id)

                if "playing" == state:
                    icon_name = "pause"
                else:
                    icon_name = "play"
            elif "media_stop" == service:
                icon_name = "stop"
            elif "volume_up" == service:
                icon_name = "volume-plus"
            elif "volume_down" == service:
                icon_name = "entity_id, volume-minus"
            elif "media_next_track" == service:
                icon_name = "skip-next"
            elif "media_previous_track" == service:
                icon_name = "skip-previous"
            else:
                log.warning(f"Icon not found for domain {domain} and service {service}")
                icon_name = "alert-circle"

            icon = self._get_icon_svg(icon_name)

            color = COLOR_ON
        else:
            # use icon of entity
            domain = entity_id.split(".")[0]

            entity = self._entities[domain].get(entity_id)

            icon_text = entity.get("icon", "None")
            icon = self._get_icon_svg(icon_text)

            if not state:
                state = self.get_state(entity_id)

            color = COLOR_ON if "on" == state else COLOR_OFF

        return (
            icon.replace("<path", f"<path {MDI_TRANSFORM}")
            .replace("<scale>", str(ICON_SCALE))
            .replace("<color>", color)
        )

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

    def get_entity(self, entity_id: str):
        if not entity_id or not "." in entity_id:
            return {}

        domain = entity_id.split(".")[0]
        return self._entities[domain].get(entity_id, {})

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
                "icon": entity.get("attributes", {}).get("icon", ""),
                "friendly_name": entity.get("attributes", {}).get("friendly_name", ""),
                "keys": {},
                "subscription_id": -1,
            }

        if self._entities:
            # entities were already loaded; keep keys and subscription ids
            for domain in self._entities.keys():
                for entity_id, entity_settings in self._entities[domain].items():
                    if entities.get(domain, {}).get(entity_id):
                        entities[domain][entity_id]["keys"] = self._entities[domain][entity_id].get("keys", {})
                        entities[domain][entity_id]["subscription_id"] = self._entities[domain][entity_id].get("subscription_id", -1)

        self._domains = domains
        self._entities = entities

    def get_services(self, domain: str) -> list:
        if not self.connect() or not domain:
            return []

        if self._services:
            return self._services.get(domain, [])

        message = self.create_message("get_services")

        response = self._send_and_wait_for_response(message)

        success = _get_field_from_message(response, FIELD_SUCCESS)

        self._services = {}

        if not success:
            log.error("Error retrieving services.")
            return []

        result: Dict[str, dict] = _get_field_from_message(response, FIELD_RESULT)

        for remote_domain in result:
            self._services[remote_domain] = list(
                result.get(remote_domain, {}).keys()
            )

        return self._services.get(domain, [])

    def call_service(self, entity_id: str, service: str) -> None:
        if not self.connect():
            return

        domain = entity_id.split(".")[0]

        message = self.create_message("call_service")
        message["domain"] = domain
        message["service"] = service
        message["target"] = {ENTITY_ID: entity_id}

        response = self._send_and_wait_for_response(message)

        success = _get_field_from_message(response, FIELD_SUCCESS)

        if not success:
            log.error(f"Error calling service {service} for entity {entity_id}.")

    def create_message(self, message_type: str) -> Dict[str, Any]:
        self._message_id += 1
        return {ID: self._message_id, FIELD_TYPE: message_type}

    def add_tracked_entity(self, entity_id: str, action_uid: str, action_entity_updated: Callable) -> None:
        if not self.connect() or not entity_id:
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
        if not self.connect():
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
        return self._connection_state == CONNECTED
        # if not self._websocket or not self._websocket.connected or not self._changes_websocket or not self._changes_websocket.connected:
        #     return False
        #
        # try:
        #     message = self.create_message("ping")
        #     response = self._send_and_wait_for_response(message)
        #
        #     return _get_field_from_message(response, FIELD_TYPE) == "pong"
        # except TimeoutError:
        #     # The connection is closed or the ping wasn't answered in time
        #     return False

    def _get_icon_svg(self, name: str) -> str:
        if "mdi:" in name:
            name = name.replace("mdi:", "")

        path = self._mdi_icons.get(name, "")

        if not path:
            path = MDI_DEFAULT_PATH

        return f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 24 24"><title>{name}</title><path d="{path}" /></svg>'

    def _send_and_wait_for_response(self, message: Dict[str, str | int]) -> str:
        WEBSOCKET_SEMAPHORE.acquire()

        self._websocket.send(json.dumps(message))

        response = self._websocket.recv()

        WEBSOCKET_SEMAPHORE.release()

        return response

    def get_connection_state(self) -> str:
        return self._connection_state

    def _keep_alive(self):
        while True:
            sleep(PING_INTERVAL)
            try:
                self._websocket.ping()
            except Exception as e:
                log.error("Ping error: ", e)
                return


def _get_field_from_message(message: str, field: str) -> Any:
    try:
        parsed = json.loads(message)

        return parsed.get(field, "")
    except json.JSONDecodeError:
        log.error(f"Could not parse {message}")
        return ""
