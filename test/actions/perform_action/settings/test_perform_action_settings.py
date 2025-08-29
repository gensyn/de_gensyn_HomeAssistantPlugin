import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action import perform_const
from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_settings import PerformActionSettings
from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_settings import DEFAULT_SETTINGS


class TestPerformActionSettingsInit(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_init_with_default(self, super_init_mock):
        action_mock = Mock()

        settings = {
            "other_setting": {
                "key": "value",
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        settings_expected = deepcopy(settings)
        settings_expected[perform_const.SETTING_ACTION] = deepcopy(DEFAULT_SETTINGS)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = PerformActionSettings(action_mock)

        self.assertEqual(settings_expected, instance._action.get_settings())
        super_init_mock.assert_called_once_with(instance,
                                                action_mock)  # only called with instance because of autospec=True
        action_mock.set_settings.assert_called_once_with(settings_expected)

    @patch('de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    @patch('de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.reset')
    def test_perform_action_settings_success(self, super_reset_mock, super_init_mock):
        action_mock = Mock()

        action = "turn_on"
        parameters = {"brightness": 30, "delay": "yes"}

        settings = {
            perform_const.SETTING_ACTION: {
                perform_const.SETTING_ACTION: action,
                perform_const.ACTION_PARAMETERS: parameters
            },
        }
        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        # test init
        instance = PerformActionSettings(action_mock)

        self.assertEqual(settings, instance._action.get_settings())
        super_init_mock.assert_called_once_with(instance,
                                                action_mock)  # only called with instance because of autospec=True

        # test get_action
        self.assertEqual(action, instance.get_action())

        # test get_parameters
        self.assertEqual(parameters, instance.get_parameters())

        # test set_parameter
        expected_settings_set_parameter = deepcopy(settings)
        expected_settings_set_parameter[perform_const.SETTING_ACTION][perform_const.ACTION_PARAMETERS]["color"] = "blue"

        instance.set_parameter("color", "blue")

        self.assertEqual(expected_settings_set_parameter, instance._action.get_settings())
        action_mock.set_settings.assert_called_once_with(expected_settings_set_parameter)

        # test remove_parameter
        action_mock.set_settings.reset_mock()
        expected_settings_remove_parameter = deepcopy(expected_settings_set_parameter)
        expected_settings_remove_parameter[perform_const.SETTING_ACTION][perform_const.ACTION_PARAMETERS].pop("delay")

        instance.remove_parameter("delay")

        self.assertEqual(expected_settings_remove_parameter, instance._action.get_settings())
        action_mock.set_settings.assert_called_once_with(expected_settings_remove_parameter)

        # test clear_parameters
        action_mock.set_settings.reset_mock()
        expected_settings_clear_parameters = deepcopy(expected_settings_remove_parameter)
        expected_settings_clear_parameters[perform_const.SETTING_ACTION][perform_const.ACTION_PARAMETERS] = {}

        instance.clear_parameters()

        self.assertEqual(expected_settings_clear_parameters, instance._action.get_settings())
        action_mock.set_settings.assert_called_once_with(expected_settings_clear_parameters)

        # test reset
        domain = "light"
        action_mock.set_settings.reset_mock()
        expected_settings_reset = {
            perform_const.SETTING_ACTION: {
                perform_const.SETTING_ACTION: perform_const.EMPTY_STRING,
                perform_const.ACTION_PARAMETERS: {}
            }
        }

        instance.reset(domain)

        super_reset_mock.assert_called_once_with(domain)
        self.assertEqual(expected_settings_reset, instance._action.get_settings())
        action_mock.set_settings.assert_called_once_with(expected_settings_reset)


if __name__ == '__main__':
    unittest.main()
