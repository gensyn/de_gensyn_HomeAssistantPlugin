import sys
import unittest
from pathlib import Path
from unittest.mock import patch


absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction
from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_settings import PerformActionSettings


class TestPerformActionInit(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_init_field_not_in_parameters_not_required(self, home_assistant_action_core_init_mock):
        test_arg = "test_arg_value"
        test_kwarg = "test_kwarg_value"

        PerformAction(test_arg, test_kwarg=test_kwarg)

        home_assistant_action_core_init_mock.assert_called_once_with(test_arg, settings_implementation=PerformActionSettings, track_entity=False, test_kwarg=test_kwarg)

