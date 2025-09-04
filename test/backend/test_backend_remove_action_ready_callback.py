import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendRemoveActionReadyCallback(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_remove_action_ready_callback_success(self, _):
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._action_ready_callbacks = {"123", "321", "213"}
        instance.remove_action_ready_callback("321")

        self.assertEqual({"123", "213"}, instance._action_ready_callbacks)

