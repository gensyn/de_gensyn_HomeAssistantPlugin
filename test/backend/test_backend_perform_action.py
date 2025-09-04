import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendCallAction(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected')
    def test_perform_action_not_connected(self, is_connected_mock, _):
        send_mock = Mock()

        websocket_mock = Mock()
        websocket_mock.send = send_mock

        is_connected_mock.return_value = False

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance.perform_action("light", "turn_on", "light.living_room", {"brightness": 100})

        send_mock.assert_not_called()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected')
    def test_perform_action_success(self, is_connected_mock, _):
        send_mock = Mock()

        create_message_mock = Mock()
        create_message_mock.return_value = {}

        websocket_mock = Mock()
        websocket_mock.send = send_mock
        websocket_mock.create_message = create_message_mock

        is_connected_mock.return_value = True

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance.perform_action("light", "turn_on", "light.living_room", {"brightness": 100})

        send_mock.assert_called_once_with({
            backend_const.DOMAIN: "light",
            backend_const.SERVICE: "turn_on",
            backend_const.TARGET: {backend_const.ENTITY_ID: "light.living_room"},
            backend_const.SERVICE_DATA: {"brightness": 100}
        })

