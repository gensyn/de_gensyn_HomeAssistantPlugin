import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackendLoadEntities(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.log.error")
    def test_load_entities_send_recv_not_successful(self, log_mock, _):
        send_and_recv_mock = Mock()
        send_and_recv_mock.return_value = (False, {}, "test_error")

        websocket_mock = Mock()
        websocket_mock.send_and_recv = send_and_recv_mock

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._load_entities()

        send_and_recv_mock.assert_called_once_with(const.GET_STATES)
        log_mock.assert_called_once_with(const.ERROR_STATES.format("test_error"))
        self.assertEqual({}, instance._entities)

    @patch.object(HomeAssistantBackend, 'connect')
    def test_load_entities_success(self, _):
        existing_entities = {
            "light": {"light.living_room": {const.STATE: "on", const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, const.ACTIONS: {"123"}, const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {const.STATE: "23", const.ATTRIBUTES: {"unit_of_measurement": "°C", "friendly_name": "Temperature Sensor"}, const.ACTIONS: {"321"}, const.SUBSCRIPTION_ID: 3}}
        }

        updated_entities = [
            {const.ENTITY_ID: "light.living_room", const.STATE: const.OFF, const.ATTRIBUTES: {"friendly_name": "Living Room Light"}},
            {const.ENTITY_ID: "sensor.humidity", const.STATE: "45", const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}}
        ]

        send_and_recv_mock = Mock()
        send_and_recv_mock.return_value = (True, updated_entities, const.EMPTY_STRING)

        websocket_mock = Mock()
        websocket_mock.send_and_recv = send_and_recv_mock

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._entities = existing_entities
        instance._websocket = websocket_mock
        instance._load_entities()

        expected_entities = {
            "light": {"light.living_room": {const.STATE: const.OFF, const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, const.ACTIONS: {"123"}, const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.humidity": {const.STATE: "45", const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}, const.ACTIONS: set(), const.SUBSCRIPTION_ID: -1}}
        }

        send_and_recv_mock.assert_called_once_with(const.GET_STATES)
        self.assertEqual(expected_entities, instance._entities)


if __name__ == '__main__':
    unittest.main()
