import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket, _on_error


class TestWebsocketInit(unittest.TestCase):

    @patch.object(HomeAssistantWebsocket, '_on_message')
    @patch.object(HomeAssistantWebsocket, '_on_close')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.__init__")
    def test_init(self, websocket_app_mock, on_close_mock, on_message_mock):
        url = "localhost"
        token = "abc"
        verify_certificate = True
        on_event_message = Mock()
        on_connected = Mock()
        on_close = Mock()
        instance = HomeAssistantWebsocket(url, token, verify_certificate, on_event_message, on_connected, on_close)

        self.assertEqual(url, instance._url)
        self.assertEqual(token, instance._token)
        self.assertEqual(verify_certificate, instance._verify_certificate)
        self.assertEqual(on_event_message, instance._on_event_message)
        self.assertEqual(on_connected, instance._on_connected_callback)
        self.assertEqual(on_close, instance._on_close_callback)
        self.assertFalse(instance.connected)
        self.assertEqual(0, instance._message_id)

        websocket_app_mock.assert_called_once_with(url=url,
                                                   on_message=on_message_mock,
                                                   on_error=_on_error,
                                                   on_close=on_close_mock)


if __name__ == '__main__':
    unittest.main()
