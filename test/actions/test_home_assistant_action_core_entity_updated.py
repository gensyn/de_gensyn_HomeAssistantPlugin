import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.home_assistant_action_core import HomeAssistantActionCore


class TestHomeAssistantActionCoreEntityUpdated(unittest.TestCase):

    @patch.object(HomeAssistantActionCore, "_create_ui_elements")
    @patch.object(HomeAssistantActionCore, "_create_event_assigner")
    def test_entity_updated_success(self, _, __):
        # This test checks if the _entity_updated method can be called without errors
        instance = HomeAssistantActionCore(True)
        instance.refresh()


if __name__ == '__main__':
    unittest.main()
