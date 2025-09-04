import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreGetConfigRows(unittest.TestCase):

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_get_config_rows_success(self, _, __):
        instance = BaseCore(Mock(), True)
        self.assertRaises(NotImplementedError, instance.get_config_rows)

