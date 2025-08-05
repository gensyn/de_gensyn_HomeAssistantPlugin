import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestBackend(unittest.TestCase):

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.json.loads")
    def test_on_message_empty_message(self, json_mock):
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, None, None, None)
        instance._on_message(None, const.EMPTY_STRING)

        json_mock.assert_not_called()

    @patch.object(HomeAssistantWebsocket, '_auth')
    def test_on_message_event_message(self, auth_mock):
        on_event_message_mock = Mock()

        message = {const.FIELD_TYPE: const.FIELD_EVENT}
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, on_event_message_mock, None,
                                          None)
        instance._on_message(None, json.dumps(message))

        on_event_message_mock.assert_called_once_with(message)
        auth_mock.assert_not_called()

    @patch.object(HomeAssistantWebsocket, '_auth')
    def test_on_message_auth_message(self, auth_mock):
        on_event_message_mock = Mock()

        message = {const.FIELD_TYPE: const.AUTH_REQUIRED}
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, on_event_message_mock, None,
                                          None)
        instance._on_message(None, json.dumps(message))

        on_event_message_mock.assert_not_called()
        auth_mock.assert_called_once()

    @patch.object(HomeAssistantWebsocket, '_auth')
    def test_on_message_other_message(self, auth_mock):
        on_event_message_mock = Mock()

        message = {const.FIELD_TYPE: const.AUTH}
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, on_event_message_mock, None,
                                          None)
        instance._on_message(None, json.dumps(message))

        on_event_message_mock.assert_not_called()
        auth_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
