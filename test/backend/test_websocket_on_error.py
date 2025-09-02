import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import backend_const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import _on_error


class TestWebsocketOnError(unittest.TestCase):

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.log.error")
    def test_log_error(self, log_mock):
        error = Exception("Test error")
        _on_error(None, error)
        log_mock.assert_called_once_with(backend_const.ERROR_GENERIC.format(error))


if __name__ == '__main__':
    unittest.main()
