import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendOnConnect(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, '_load_entities')
    @patch.object(HomeAssistantBackend, '_load_actions')
    @patch.object(HomeAssistantBackend, '_readd_tracked_entities')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.log.info")
    def test_on_connect_success(self, log_mock, readd_tracked_entities_mock, load_actions_mock, load_entities_mock, _):
        connection_status_callback_mock = Mock()

        ready_mock = Mock()

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._connection_status_callback = connection_status_callback_mock
        instance._action_ready_callbacks = [ready_mock] * 2

        instance._on_connect()

        connection_status_callback_mock.assert_called_once_with(backend_const.CONNECTED)
        log_mock.assert_called_once_with("Connected to Home Assistant")
        load_entities_mock.assert_called_once()
        load_actions_mock.assert_called_once()
        readd_tracked_entities_mock.assert_called_once()
        self.assertEqual(2, ready_mock.call_count)

