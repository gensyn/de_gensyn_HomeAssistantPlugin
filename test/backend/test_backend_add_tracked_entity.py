import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendAddTrackedEntity(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_add_tracked_entity_no_entity(self, _):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        instance.add_tracked_entity(backend_const.EMPTY_STRING, "123")

        self.assertEqual(set(), instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(-1, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=False)
    def test_add_tracked_entity_not_connected(self, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        instance.add_tracked_entity("light.living_room", None)

        self.assertEqual(set(), instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(-1, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    @patch.object(HomeAssistantBackend, '_load_entities')
    def test_add_tracked_entity_entity_non_existent(self, load_entities_mock, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}
        }

        load_entities_mock.side_effect = lambda: setattr(instance, '_entities', entities)

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)

        instance.add_tracked_entity("light.kitchen", None)

        self.assertEqual(set(), instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(-1, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_add_tracked_entity_action_already_registered(self, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: {"123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        instance.add_tracked_entity("light.living_room", "123")

        self.assertEqual({"123"}, instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(2, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_add_tracked_entity_already_subscribed_to_entity(self, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: {"123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        instance.add_tracked_entity("light.living_room", "321")

        self.assertEqual({"123", "321"}, instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(2, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_add_tracked_entity_success(self, _, __):
        create_message_mock = Mock()
        create_message_mock.return_value = {backend_const.ID: 3}

        send_mock = Mock()

        websocket_mock = Mock()
        websocket_mock.create_message = create_message_mock
        websocket_mock.send = send_mock

        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._entities = entities

        instance.add_tracked_entity("light.living_room", "123")

        create_message_mock.assert_called_once()
        send_mock.assert_called_once_with(
            {backend_const.ID: 3, backend_const.TRIGGER: {backend_const.PLATFORM: backend_const.STATE, backend_const.ENTITY_ID: "light.living_room"}})
        self.assertEqual({"123"}, instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(3, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

