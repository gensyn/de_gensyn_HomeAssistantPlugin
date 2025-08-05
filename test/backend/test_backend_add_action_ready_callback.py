import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackendAddActionReadyCallback(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_add_action_ready_callback_success(self, _):
        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)

        instance.add_action_ready_callback("123")
        instance.add_action_ready_callback("321")

        self.assertEqual({"123", "321"}, instance._action_ready_callbacks)


if __name__ == '__main__':
    unittest.main()
