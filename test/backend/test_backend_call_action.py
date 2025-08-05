import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackend(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected')
    def test_call_action_not_connected(self, is_connected_mock, _):
        send_mock = Mock()

        websocket_mock = Mock()
        websocket_mock.send = send_mock

        is_connected_mock.return_value = False

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance.call_action("light.living_room", "turn_on", {"brightness": 100})

        send_mock.assert_not_called()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected')
    def test_call_action_success(self, is_connected_mock, _):
        send_mock = Mock()

        create_message_mock = Mock()
        create_message_mock.return_value = {}

        websocket_mock = Mock()
        websocket_mock.send = send_mock
        websocket_mock.create_message = create_message_mock

        is_connected_mock.return_value = True

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance.call_action("light.living_room", "turn_on", {"brightness": 100})

        send_mock.assert_called_once_with({
            const.DOMAIN: "light",
            const.SERVICE: "turn_on",
            const.TARGET: {const.ENTITY_ID: "light.living_room"},
            const.SERVICE_DATA: {"brightness": 100}
        })


if __name__ == '__main__':
    unittest.main()
