import sys
import unittest
from pathlib import Path
from ssl import CERT_NONE
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketRunForever(unittest.TestCase):

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.run_forever")
    def test_run_forever_verify_certificate(self, websocket_app_mock):
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, None, None, None)
        instance.run_forever()

        websocket_app_mock.assert_called_once_with(sslopt={}, reconnect=const.RECONNECT_INTERVAL)

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.run_forever")
    def test_run_forever_dont_verify_certificate(self, websocket_app_mock):
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, False, None, None, None)
        instance.run_forever()

        websocket_app_mock.assert_called_once_with(sslopt={const.CERT_REQS: CERT_NONE}, reconnect=const.RECONNECT_INTERVAL)


if __name__ == '__main__':
    unittest.main()
