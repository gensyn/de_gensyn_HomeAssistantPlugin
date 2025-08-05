import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackendLoadActions(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.log.error")
    def test_load_actions_send_recv_not_successful(self, log_mock, _):
        send_and_recv_mock = Mock()
        send_and_recv_mock.return_value = (False, {}, "test_error")

        websocket_mock = Mock()
        websocket_mock.send_and_recv = send_and_recv_mock

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._load_actions()

        send_and_recv_mock.assert_called_once_with(const.GET_SERVICES)
        log_mock.assert_called_once_with(const.ERROR_SERVICES.format("test_error"))
        self.assertEqual({}, instance._actions)

    @patch.object(HomeAssistantBackend, 'connect')
    def test_load_actions_success(self, _):
        actions = {
            "light": {
                "turn_on": {
                    "fields": {
                        "brightness": {"selector": {"number": {"min": 0, "max": 255}}},
                        "color_temp": {"selector": {"number": {"min": 153, "max": 500}}},
                    }
                },
                "turn_off": {}
            },
            "switch": {
                "toggle": {"fields": {
                    "delay": {"selector": {"number": {"min": 0, "max": 60}}}
                }}
            }
        }

        send_and_recv_mock = Mock()
        send_and_recv_mock.return_value = (True, actions, const.EMPTY_STRING)

        websocket_mock = Mock()
        websocket_mock.send_and_recv = send_and_recv_mock

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._load_actions()

        self.assertEqual(actions, instance._actions)


if __name__ == '__main__':
    unittest.main()
