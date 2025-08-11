import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.home_assistant_action_core import HomeAssistantActionCore


class TestHomeAssistantActionCoreReload(unittest.TestCase):

    @patch.object(HomeAssistantActionCore, "_create_ui_elements")
    @patch.object(HomeAssistantActionCore, "_create_event_assigner")
    @patch.object(HomeAssistantActionCore, "_set_enabled_disabled")
    @patch.object(HomeAssistantActionCore, "_entity_updated")
    def test_reload_success(self, entity_updated_mock, set_enabled_disabled_mock, _, __):
        settings_mock = Mock()
        settings_mock.load = Mock()

        instance = HomeAssistantActionCore(False)
        instance.settings = settings_mock
        instance._reload()

        settings_mock.load.assert_called_once()
        set_enabled_disabled_mock.assert_called_once()
        entity_updated_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
