import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row import \
    ParameterSwitchRow


class TestParameterSwitchRow(unittest.TestCase):

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow.__init__')
    def test_init(self, parameter_row_init_mock, switch_row_init_mock):
        create_instance(switch_row_init_mock, parameter_row_init_mock, False)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.get_active')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow.__init__')
    def test_get_parameter_value(self, parameter_row_init_mock, switch_row_init_mock, get_active_mock):
        instance = create_instance(switch_row_init_mock, parameter_row_init_mock, False)
        get_active_mock.return_value = False
        result = instance.get_parameter_value()

        self.assertEqual(result, False)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow.__init__')
    def test_set_value_check_not_active(self, parameter_row_init_mock, switch_row_init_mock, switch_row_set_value_mock):
        instance = create_instance(switch_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=False)
        instance.set_value(False)

        instance.check.get_active.assert_called_once()
        switch_row_set_value_mock.assert_not_called()

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow.__init__')
    def test_set_value_check_active(self, parameter_row_init_mock, switch_row_init_mock, switch_row_set_value_mock):
        instance = create_instance(switch_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=True)
        instance.set_value(True)

        instance.check.get_active.assert_called_once()
        switch_row_set_value_mock.assert_called_once_with(instance, True)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow.__init__')
    def test_value_changed_required(self, parameter_row_init_mock, parameter_row_on_change_mock, switch_row_init_mock,
                                    switch_row_value_changed_mock):
        instance = create_instance(switch_row_init_mock, parameter_row_init_mock, True)
        instance.check.set_active = Mock()
        instance._value_changed(instance, None)

        instance.check.set_active.assert_not_called()
        switch_row_value_changed_mock.assert_called_once_with(instance, instance, None)
        parameter_row_on_change_mock.assert_called_once_with(instance)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.SwitchRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row.ParameterRow.__init__')
    def test_value_changed_not_required(self, parameter_row_init_mock, parameter_row_on_change_mock,
                                        switch_row_init_mock, switch_row_value_changed_mock):
        instance = create_instance(switch_row_init_mock, parameter_row_init_mock, False)
        instance.check.set_active = Mock()
        instance._value_changed(instance, None)

        instance.check.set_active.assert_called_once_with(True)
        switch_row_value_changed_mock.assert_called_once_with(instance, instance, None)
        parameter_row_on_change_mock.assert_called_once_with(instance)


def create_instance(switch_row_init_mock, parameter_row_init_mock, required) -> ParameterSwitchRow:
    action_core_mock = Mock()
    var_name = "test_var"
    field_name = "test_field"
    default_value = "default_value"

    def add_instance_attributes(switch_row, *_, **__):
        switch_row.widget = Mock()
        switch_row.check = Mock()
        switch_row.required = required

    switch_row_init_mock.side_effect = add_instance_attributes

    instance = ParameterSwitchRow(action_core_mock, var_name, field_name, default_value, required)

    switch_row_init_mock.assert_called_once_with(instance, action_core_mock, var_name, default_value,
                                                 title=field_name, can_reset=False, complex_var_name=True)
    parameter_row_init_mock.assert_called_once_with(instance, action_core_mock, field_name, required)

    return instance

