import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.home_assistant_action_core import HomeAssistantActionCore
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.const import HOME_ASSISTANT_ACTION
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.const import PERFORM_ACTION


class TestHomeAssistantActionCoreInit(unittest.TestCase):

    @patch.object(HomeAssistantActionCore, "_create_ui_elements")
    @patch.object(HomeAssistantActionCore, "_create_event_assigner")
    def test_init_success(self, create_event_assigner_mock, create_ui_elements_mock):
        track_entity = True
        test_arg = "test_arg_value"
        test_kwarg = "test_kwarg_value"

        instance = HomeAssistantActionCore(track_entity, test_arg, test_kwarg=test_kwarg)

        self.assertIsNone(instance.settings)
        self.assertFalse(instance.initialized)
        self.assertEqual(instance.plugin_base.locale_manager, instance.lm)
        self.assertTrue(instance.has_configuration)
        self.assertEqual(track_entity, instance.track_entity)
        self.assertEqual((test_arg,), instance.args)
        self.assertEqual({"test_kwarg": test_kwarg}, instance.kwargs)
        create_ui_elements_mock.assert_called_once()
        create_event_assigner_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
