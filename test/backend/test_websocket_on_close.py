import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import backend_const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketOnClose(unittest.TestCase):

    def test_on_close_success(self):
        on_close_callback_mock = Mock()

        instance = HomeAssistantWebsocket(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, None, None,
                                          on_close_callback_mock)
        instance.connected = True
        self.assertTrue(instance.connected)
        instance._on_close(None, None, None)

        self.assertFalse(instance.connected)
        on_close_callback_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
