"""
Module for the Home Assistant backend.
"""

import json
from threading import Thread, Semaphore
from time import sleep
from ssl import CERT_NONE, SSLError, SSLEOFError
from typing import Dict, Callable, Any, List, Set, Optional

from loguru import logger as log
from websocket import (
    create_connection,
    WebSocket,
    WebSocketException,
    WebSocketAddressException,
)

from de_gensyn_HomeAssistantPlugin import const

HASS_WEBSOCKET_API = "/api/websocket?latest"

FIELD_EVENT = "event"
ENTITY_ID = "entity_id"
ID = "id"
FIELD_TYPE = "type"
FIELD_SUCCESS = "success"
FIELD_RESULT = "result"
BUTTON_ENCODE_SYMBOL = "-"
RECV_LOOP_TIMEOUT = 300
PING_INTERVAL = 30

ERRORS_TO_EXCEPT = (
    WebSocketException,
    WebSocketAddressException,
    ValueError,
    ConnectionResetError,
    BrokenPipeError,
    SSLEOFError,
)


class HomeAssistantBackend:
    """
    Defines the Home Assistant backend.
    """

    def __init__(self):
        self._websocket: Optional[WebSocket] = None
        self._changes_websocket: Optional[WebSocket] = None
        self._message_id: int = 0
        self._domains: List[str] = []
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._services: Dict[str, Dict[str, Any]] = {}
        self._host: str = ""
        self._port: str = ""
        self._ssl: bool = True
        self._verify_certificate: bool = True
        self._token: str = ""
        self._connection_status_callback: Callable = lambda _1, _2=None: None
        self._keep_alive_thread: Optional[Thread] = None
        self._reconnect_thread: Optional[Thread] = None
        self._pending_actions: List[Callable] = []
        self._entities_update_semaphore = Semaphore(1)
        self._websocket_semaphore = Semaphore(1)
        self._tracked_entities: Dict[str, Set[Callable]] = {}

    def set_host(self, host: str) -> None:
        """Set the Home Assistant host."""
        if "//" in host:
            host = host.split("//")[1]
        if self._host == host:
            return
        self._host = host

    def set_port(self, port: str) -> None:
        """Set the Home Assistant port."""
        if self._port == port:
            return
        self._port = port

    def set_ssl(self, ssl: bool) -> None:
        """Set whether Home Assistant uses SSL."""
        if self._ssl == ssl:
            return
        self._ssl = ssl

    def set_verify_certificate(self, verify_certificate: bool) -> None:
        """Set whether the certificate should be verified."""
        if self._verify_certificate == verify_certificate:
            return
        self._verify_certificate = verify_certificate

    def set_token(self, token: str) -> None:
        """Set the Home Assistant token."""
        if self._token == token:
            return
        self._token = token

    def set_connection_status_callback(self, callback: Callable) -> None:
        """Set a callback to be called when the connection state changes."""
        self._connection_status_callback = callback

    def reconnect(self) -> bool:
        """Disconnect from Home Assistant and then connect again."""
        self._disconnect()
        success = self._connect()
        if not success and self._host and self._token and self._port:
            if not self._reconnect_thread or not self._reconnect_thread.is_alive():
                self._reconnect_thread = Thread(
                    target=self._retry_connect, daemon=True
                )
                self._reconnect_thread.start()
        return success

    def _connect(self) -> bool:
        """Connect to Home Assistant."""
        if self.is_connected():
            return True

        self._connection_status_callback(const.CONNECTING)

        if not self._host or not self._token or not self._port:
            self._connection_status_callback(const.NOT_CONNECTED)
            return False

        if self._websocket and self._websocket.connected:
            self._websocket.close()
        if self._changes_websocket and self._changes_websocket.connected:
            self._changes_websocket.close()

        self._connection_status_callback(const.AUTHENTICATING)

        self._websocket = self._auth()
        if not self._websocket:
            self._connection_status_callback(const.NOT_CONNECTED)
            return False

        self._changes_websocket = self._auth()
        if not self._changes_websocket:
            self._websocket.close()
            self._connection_status_callback(const.NOT_CONNECTED)
            return False

        message = self._create_message("get_config")
        config = self._send_and_wait_for_response_with_semaphore(message)
        result: Dict[str, dict] = _get_field_from_message(config, FIELD_RESULT)

        if not result or result.get("state", "") != "RUNNING":
            # Home Assistant hasn't finished starting yet so not all entities
            # might have been initialized - try again later
            self._websocket.close()
            self._changes_websocket.close()
            self._connection_status_callback(const.NOT_CONNECTED)
            log.info("Home Assistant not fully started - retrying")
            return False

        log.info("Connected to Home Assistant")
        self._connection_status_callback(const.CONNECTED)

        Thread(target=self._async_run_recv_loop, daemon=True).start()

        if not self._keep_alive_thread or not self._keep_alive_thread.is_alive():
            self._keep_alive_thread = Thread(
                target=self._keep_alive, daemon=True
            )
            self._keep_alive_thread.start()

        with self._entities_update_semaphore:
            self._load_domains_and_entities()

        for action in self._pending_actions:
            action()
        for actions in self._tracked_entities.values():
            for action in actions:
                action()

        return True

    def _disconnect(self) -> None:
        """Disconnect from Home Assistant."""
        self._connection_status_callback(const.DISCONNECTING)

        if self._websocket and self._websocket.connected:
            self._websocket.close()
            self._websocket = None
        if self._changes_websocket and self._changes_websocket.connected:
            self._changes_websocket.close()
            self._changes_websocket = None

        self._websocket_semaphore = Semaphore(1)
        self._entities_update_semaphore = Semaphore(1)
        self._message_id = 0

        self._connection_status_callback(const.NOT_CONNECTED)

    def _auth(self) -> Optional[WebSocket]:
        websocket_host = (
            f'{"wss://" if self._ssl else "ws://"}{self._host}:{self._port}{HASS_WEBSOCKET_API}'
        )
        ssl_opt = {}
        if not self._verify_certificate:
            ssl_opt["cert_reqs"] = CERT_NONE

        try:
            new_websocket = create_connection(websocket_host, sslopt=ssl_opt)
            auth_required = new_websocket.recv()
            auth_required = _get_field_from_message(auth_required, FIELD_TYPE)
            if not auth_required:
                log.error("Could not auth with Home Assistant")
                return None

            new_websocket.send(
                json.dumps({FIELD_TYPE: "auth", "access_token": self._token})
            )
            auth_ok = new_websocket.recv()
            auth_ok = _get_field_from_message(auth_ok, FIELD_TYPE)
            if not auth_ok or auth_ok != "auth_ok":
                log.error("Could not auth with Home Assistant")
                return None
        except SSLError:
            error = "An SSL error occurred. Is the server certificate valid?"
            if self._verify_certificate:
                error += (
                    " If you are using a self-signed certificate, please disable certificate "
                    "verification in the plugin settings."
                )
            log.error(error)
            return None
        except ConnectionRefusedError:
            log.error(
                f"Connection refused by {websocket_host}. Make sure"
                f" 'websocket_api' is enabled in your Home Assistant configuration."
            )
            return None
        except ERRORS_TO_EXCEPT as e:
            log.error(f"Could not connect to {websocket_host}: {e}")
            return None

        return new_websocket

    def _async_run_recv_loop(self):
        # wait for entities update finishing
        with self._entities_update_semaphore:
            pass

        if self._entities:
            # if the connection was lost we might need to resubscribe to entity events
            for domain, domain_entry in self._entities.items():
                for entity, entity_settings in domain_entry.items():
                    if entity_settings.get("keys"):
                        action_items = entity_settings["keys"].items()
                        entity_settings["subscription_id"] = -1
                        entity_settings["keys"] = {}
                        for action_uid, action in action_items:
                            self.add_tracked_entity(entity, action_uid, action)

        while self._changes_websocket and self._changes_websocket.connected:
            try:
                message = self._changes_websocket.recv()
            except ERRORS_TO_EXCEPT as e:
                log.info(f"Connection closed; quitting recv() loop: {e}")
                break

            if not message:
                # received an empty message - happens when Home Assistants shuts down; ignore
                continue

            message_type = _get_field_from_message(message, FIELD_TYPE)
            if FIELD_EVENT == message_type:
                new_state = (
                    json.loads(message)
                    .get(FIELD_EVENT, {})
                    .get("variables", {})
                    .get("trigger", {})
                    .get("to_state", {})
                )
                if not new_state:
                    entity_id = (
                        json.loads(message)
                        .get(FIELD_EVENT, {})
                        .get("variables", {})
                        .get("trigger", {})
                        .get("from_state", {})
                        .get(ENTITY_ID)
                    )
                    entity_settings = self._entities[entity_id.split(".")[0]].get(entity_id)
                    actions = entity_settings.get("keys", {}).values()
                    for action_entity_updated in actions:
                        action_entity_updated()
                    return

                entity_id = new_state.get(ENTITY_ID)
                domain = entity_id.split(".")[0]
                entity_settings = self._entities[domain].get(entity_id)
                actions = entity_settings.get("keys", {}).values()
                state = new_state.get(const.STATE)
                attributes = new_state.get(const.ATTRIBUTES, {})

                self._entities[domain][entity_id][const.STATE] = state
                self._entities[domain][entity_id][const.ATTRIBUTES] = attributes

                update_state = {
                    const.STATE: state,
                    const.ATTRIBUTES: attributes,
                    const.HA_CONNECTED: self.is_connected(),
                }
                for action_entity_updated in actions:
                    action_entity_updated(update_state)

        self._disconnect()
        for actions in self._tracked_entities.values():
            for action in actions:
                action()

        if not self._reconnect_thread or not self._reconnect_thread.is_alive():
            self._reconnect_thread = Thread(
                target=self._retry_connect, daemon=True
            )
            self._reconnect_thread.start()

    def get_domains(self) -> List[str]:
        """Get a list of all domains known to Home Assistant."""
        if not self._connect():
            return []
        if not self._domains:
            self._load_domains_and_entities()
        return self._domains

    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Return the entity state with the requested name."""
        entity_fallback_dict = {
            const.STATE: "N/A",
            const.ATTRIBUTES: {},
            const.HA_CONNECTED: self.is_connected(),
        }
        if not entity_id or "." not in entity_id:
            return entity_fallback_dict

        domain = entity_id.split(".")[0]
        entity_dict = self._entities.get(domain, {}).get(entity_id, entity_fallback_dict)
        entity_dict[const.HA_CONNECTED] = self.is_connected()
        return entity_dict

    def get_entities(self, domain: str) -> List[str]:
        """Return a list of all entities known to Home Assistant."""
        if not self._connect() or not domain:
            return []
        if not self._entities:
            self._load_domains_and_entities()
        return list(self._entities.get(domain, {}).keys())

    def _load_domains_and_entities(self) -> None:
        """Loads the domains and entities from Home Assistant."""
        message = self._create_message("get_states")
        response = self._send_and_wait_for_response_with_semaphore(message)
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
            for domain, domain_entry in self._entities.items():
                for entity_id in domain_entry.keys():
                    if entities.get(domain, {}).get(entity_id):
                        entities[domain][entity_id]["keys"] = domain_entry[entity_id].get(
                            "keys", {}
                        )
                        entities[domain][entity_id]["subscription_id"] = domain_entry[
                            entity_id
                        ].get("subscription_id", -1)

        self._domains = domains
        self._entities = entities

    def get_services(self, domain: str) -> Dict[str, Dict[str, Any]]:
        """Return all services known to Home Assistant."""
        if not self._connect() or not domain:
            return {}
        if self._services:
            return self._services.get(domain, {})

        message = self._create_message("get_services")
        response = self._send_and_wait_for_response_with_semaphore(message)
        success = _get_field_from_message(response, FIELD_SUCCESS)
        self._services = {}

        if not success:
            log.error("Error retrieving services.")
            return {}

        self._services = _get_field_from_message(response, FIELD_RESULT)
        return self._services.get(domain, {})

    def call_service(
        self, entity_id: str, service: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Calls a Home Assistant service."""
        if not self._connect():
            return

        domain = entity_id.split(".")[0]
        message = self._create_message("call_service")
        message["domain"] = domain
        message["service"] = service
        message["target"] = {ENTITY_ID: entity_id}
        message["service_data"] = data if data else {}

        response = self._send_and_wait_for_response_with_semaphore(message)
        success = _get_field_from_message(response, FIELD_SUCCESS)

        if not success:
            # try one more time
            response = self._send_and_wait_for_response_with_semaphore(message)
            success = _get_field_from_message(response, FIELD_SUCCESS)
            if not success:
                log.error(f"Error calling service {service} for entity {entity_id}.")

    def _create_message(self, message_type: str) -> Dict[str, Any]:
        """Create a message that can be sent to the Home Assistant websocket."""
        self._message_id += 1
        return {ID: self._message_id, FIELD_TYPE: message_type}

    def add_tracked_entity(
        self, entity_id: str, action_uid: str, action_entity_updated: Callable
    ) -> None:
        """Register an entity with the Home Assistant websocket to be notified when the entity is updated."""
        if not entity_id or not self._connect():
            return

        domain = entity_id.split(".")[0]
        if not self._entities:
            self._load_domains_and_entities()

        entity_settings = self._entities.get(domain, {}).get(entity_id)
        if not entity_settings:
            # entity doesn't exist (anymore)
            return

        if action_uid in entity_settings.get("keys", {}).keys():
            # key already registered
            return

        actions = self._tracked_entities.get(entity_id, set())
        actions.add(action_entity_updated)
        self._tracked_entities[entity_id] = actions

        entity_settings.get("keys")[action_uid] = action_entity_updated

        if entity_settings.get("subscription_id") > -1:
            # already subscribed to entity events
            return

        message = self._create_message("subscribe_trigger")
        message["trigger"] = {"platform": "state", ENTITY_ID: entity_id}
        self._changes_websocket.send(json.dumps(message))
        entity_settings["subscription_id"] = message.get(ID)

    def remove_tracked_entity(self, entity_id: str, action_uid: str) -> None:
        """Deregister a previously registered entity."""
        if not entity_id or not self._connect():
            return

        domain = entity_id.split(".")[0]
        entity_settings = self._entities[domain].get(entity_id, {})
        entity_settings.get("keys", {}).pop(action_uid, None)

        if len(entity_settings.get("keys", {})) > 0:
            # the entity is still attached to another key, so keep the trigger subscription
            return

        message = self._create_message("unsubscribe_events")
        message["subscription_id"] = entity_settings["subscription_id"]
        self._changes_websocket.send(json.dumps(message))
        entity_settings["subscription_id"] = -1
        self._tracked_entities.pop(entity_id, None)

    def is_connected(self) -> bool:
        """Return whether a connection to Home Assistant is established."""
        return self._websocket is not None and self._websocket.connected

    def _send_and_wait_for_response_with_semaphore(
        self, message: Dict[str, Any], try_count: int = 0
    ) -> str:
        """Send a websocket message to Home Assistant and return the response using a semaphore."""
        with self._websocket_semaphore:
            return self._send_and_wait_for_response(message, try_count)

    def _send_and_wait_for_response(
        self, message: Dict[str, Any], try_count: int
    ) -> str:
        """Send a websocket message to Home Assistant and return the response."""
        self._message_id += 1
        message[ID] = self._message_id

        try:
            self._websocket.send(json.dumps(message))
        except ERRORS_TO_EXCEPT as e:
            connected = self.reconnect()
            if connected:
                self._websocket.send(json.dumps(message))
            else:
                log.error(f"({e}) Cannot send message {message}")
                return const.EMPTY_STRING
        try:
            return self._websocket.recv()
        except ERRORS_TO_EXCEPT as e:
            log.error(f"Error: {e}")
            self.reconnect()
            if try_count < 3:
                return self._send_and_wait_for_response(message, try_count + 1)
        log.error(f"Cannot send message {message}")
        return const.EMPTY_STRING

    def _keep_alive(self):
        """Periodically ping the Home Assistant server to keep the websocket connection alive."""
        while True:
            sleep(PING_INTERVAL)
            if not self._websocket:
                return
            try:
                self._websocket.ping()
            except ERRORS_TO_EXCEPT as e:
                self._connection_status_callback(const.NOT_CONNECTED)
                log.info(f"Disconnected from Home Assistant: {e}")
                return

    def _retry_connect(self):
        """Periodically try to connect to the Home Assistant server."""
        log.info("Trying to reconnect to Home Assistant")
        while not self._connect():
            self._connection_status_callback(const.WAITING_FOR_RETRY)
            sleep(10)

    def register_action(self, action: Callable) -> None:
        """Register an action to be called when a connection to Home Assistant has been established."""
        if action not in self._pending_actions:
            self._pending_actions.append(action)

    def remove_action(self, action: Callable) -> None:
        """Remove a previously registered action."""
        if action in self._pending_actions:
            self._pending_actions.remove(action)

    def create_url(self, resource: str) -> Optional[str]:
        """Creates the URL for a specific resource on the HA host."""
        if not self._host or not resource:
            return None

        schema = "https://" if self._ssl else "http://"
        host = self._host.rstrip("/")
        resource = resource.lstrip("/")

        return f"{schema}{host}:{self._port}/{resource}"


def _get_field_from_message(message: str, field: str) -> Any:
    """Extracts the specified field from the message."""
    if not message:
        return ""
    try:
        parsed = json.loads(message)
        return parsed.get(field, "")
    except json.JSONDecodeError:
        log.error(f"Could not parse {message}")
        return ""