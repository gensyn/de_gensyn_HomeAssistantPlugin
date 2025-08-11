import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.home_assistant_action_core import HomeAssistantActionCore


class TestHomeAssistantActionCoreCreateEventAssigner(unittest.TestCase):

    @patch.object(HomeAssistantActionCore, "_create_ui_elements")
    def test_create_event_assigner_success(self, _):
        # This test checks if the _create_event_assigner method can be called without errors
        with patch.object(HomeAssistantActionCore, "_create_event_assigner"):
            instance = HomeAssistantActionCore(True)
        instance._create_event_assigner()


if __name__ == '__main__':
    unittest.main()
