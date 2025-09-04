import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendOnDisconnect(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.log.info")
    def test_on_disconnect_wrong_websocket(self, log_mock, _):
        wrong_mock = Mock()
        right_mock = Mock()

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = right_mock
        instance._on_disconnect(wrong_mock)

        log_mock.assert_not_called()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.sleep")
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.log.info")
    def test_on_disconnect_websocket_changed_during_sleep(self, log_mock, sleep_mock, connect_mock):
        action_mock = Mock()
        action_ready_callbacks = [action_mock] * 3
        websocket_mock = Mock()

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._action_ready_callbacks = action_ready_callbacks
        sleep_mock.side_effect = lambda x: setattr(instance, '_websocket', Mock())
        instance._on_disconnect(websocket_mock)

        log_mock.assert_called_once_with(backend_const.INFO_DISCONNECTED)
        self.assertEqual(3, action_mock.call_count)
        sleep_mock.assert_called_once_with(backend_const.RECONNECT_INTERVAL)
        self.assertEqual(1, connect_mock.call_count)  # called once during instantiation

    @patch.object(HomeAssistantBackend, 'connect')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.sleep")
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.log.info")
    def test_on_disconnect_success(self, log_mock, sleep_mock, connect_mock):
        action_mock = Mock()
        action_ready_callbacks = [action_mock] * 3
        websocket_mock = Mock()

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._action_ready_callbacks = action_ready_callbacks
        instance._on_disconnect(websocket_mock)

        log_mock.assert_called_once_with(backend_const.INFO_DISCONNECTED)
        self.assertEqual(3, action_mock.call_count)
        sleep_mock.assert_called_once_with(backend_const.RECONNECT_INTERVAL)
        self.assertEqual(2, connect_mock.call_count)  # called once during instantiation and once during disconnect

