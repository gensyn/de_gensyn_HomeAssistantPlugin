import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreReload(unittest.TestCase):

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_set_enabled_disabled")
    @patch.object(BaseCore, "refresh")
    def test_reload_success(self, refresh_mock, set_enabled_disabled_mock, _, __):
        settings_mock = Mock()
        settings_mock.load = Mock()

        instance = BaseCore(False)
        instance.initialized = True
        instance.settings = settings_mock
        instance._reload()

        settings_mock.load.assert_called_once()
        set_enabled_disabled_mock.assert_called_once()
        refresh_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
