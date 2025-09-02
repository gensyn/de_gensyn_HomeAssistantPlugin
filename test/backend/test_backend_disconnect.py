import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendDisconnect(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_disconnect_success(self,_):
        websocket_close_mock = Mock()

        websocket_mock = Mock()
        websocket_mock.connected = True
        websocket_mock.close = websocket_close_mock

        callback_mock = Mock()

        instance = HomeAssistantBackend("localhost", "8123", True, True, "abc")
        instance._connection_status_callback = callback_mock
        instance._websocket = websocket_mock

        instance.disconnect()

        self.assertFalse(websocket_mock.connected)
        websocket_close_mock.assert_called_once()
        self.assertIsNone(instance._websocket)
        callback_mock.assert_called_once_with(backend_const.NOT_CONNECTED)


if __name__ == '__main__':
    unittest.main()
