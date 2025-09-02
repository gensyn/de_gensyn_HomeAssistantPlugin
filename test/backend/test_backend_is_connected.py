import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendIsConnected(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_is_connected_no_websocket(self, _):
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)

        result = instance.is_connected()

        self.assertFalse(result)

    @patch.object(HomeAssistantBackend, 'connect')
    def test_is_connected_not_connected(self, _):
        websocket_mock = Mock()
        websocket_mock.connected = False

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock

        result = instance.is_connected()

        self.assertFalse(result)

    @patch.object(HomeAssistantBackend, 'connect')
    def test_is_connected_success(self, _):
        websocket_mock = Mock()
        websocket_mock.connected = True

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock

        result = instance.is_connected()

        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
