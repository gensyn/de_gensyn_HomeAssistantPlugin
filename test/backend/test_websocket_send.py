import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketSend(unittest.TestCase):

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.send")
    def test_send_not_connected_with_check(self, send_mock):
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, None, None, None)
        instance.send({const.FIELD_TYPE: const.FIELD_EVENT})
        send_mock.assert_not_called()

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.send")
    def test_send_send_without_check(self, send_mock):
        message = {const.FIELD_TYPE: const.FIELD_EVENT}
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, None, None, None)
        instance.send({const.FIELD_TYPE: const.FIELD_EVENT}, check_connected=False)
        send_mock.assert_called_once_with(json.dumps(message))

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.send")
    def test_send_send_with_check(self, send_mock):
        message = {const.FIELD_TYPE: const.FIELD_EVENT}
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, None, None, None)
        instance.connected = True
        instance.send({const.FIELD_TYPE: const.FIELD_EVENT})
        send_mock.assert_called_once_with(json.dumps(message))

if __name__ == '__main__':
    unittest.main()
