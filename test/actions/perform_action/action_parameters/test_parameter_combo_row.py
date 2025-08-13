import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row import ParameterComboRow


class TestParameterComboRow(unittest.TestCase):

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow.__init__')
    def test_init(self, parameter_row_init_mock, combo_row_init_mock):
        create_instance(combo_row_init_mock, parameter_row_init_mock, False)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.get_selected_item')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow.__init__')
    def test_get_parameter_value(self, parameter_row_init_mock, combo_row_init_mock, get_selected_item_mock):
        instance = create_instance(combo_row_init_mock, parameter_row_init_mock, False)
        get_selected_item_mock.return_value = "selected_item"
        result = instance.get_parameter_value()

        self.assertEqual(result, "selected_item")

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow.__init__')
    def test_set_value_check_not_active(self, parameter_row_init_mock, combo_row_init_mock, combo_row_set_value_mock):
        instance = create_instance(combo_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=False)
        instance.set_value("new_item")

        instance.check.get_active.assert_called_once()
        combo_row_set_value_mock.assert_not_called()

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow.__init__')
    def test_set_value_check_active(self, parameter_row_init_mock, combo_row_init_mock, combo_row_set_value_mock):
        instance = create_instance(combo_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=True)
        instance.set_value("new_item")

        instance.check.get_active.assert_called_once()
        combo_row_set_value_mock.assert_called_once_with(instance, "new_item")

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow.__init__')
    def test_value_changed_required(self, parameter_row_init_mock, parameter_row_on_change_mock, combo_row_init_mock,
                                    combo_row_value_changed_mock):
        instance = create_instance(combo_row_init_mock, parameter_row_init_mock, True)
        instance.check.set_active = Mock()
        instance._value_changed(instance, None)

        instance.check.set_active.assert_not_called()
        combo_row_value_changed_mock.assert_called_once_with(instance, instance, None)
        parameter_row_on_change_mock.assert_called_once_with(instance)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.get_selected_item')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ComboRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_combo_row.ParameterRow.__init__')
    def test_value_changed_not_required(self, parameter_row_init_mock, parameter_row_on_change_mock,
                                        combo_row_init_mock, combo_row_value_changed_mock, get_selected_item_mock):
        get_selected_item_mock.return_value = False
        instance = create_instance(combo_row_init_mock, parameter_row_init_mock, False)
        instance.check.set_active = Mock()
        instance._value_changed(instance, None)

        get_selected_item_mock.assert_called_once_with()
        instance.check.set_active.assert_called_once_with(True)
        combo_row_value_changed_mock.assert_called_once_with(instance, instance, None)
        parameter_row_on_change_mock.assert_called_once_with(instance)


def create_instance(combo_row_init_mock, parameter_row_init_mock, required) -> ParameterComboRow:
    action_core_mock = Mock()
    var_name = "test_var"
    field_name = "test_field"
    default_value = "default_value"
    items = ["item1", "item2"]

    def add_instance_attributes(combo_row, *_, **__):
        combo_row.widget = Mock()
        combo_row.check = Mock()
        combo_row.required = required

    combo_row_init_mock.side_effect = add_instance_attributes

    instance = ParameterComboRow(action_core_mock, var_name, field_name, default_value, items, required)

    combo_row_init_mock.assert_called_once_with(instance, action_core_mock, var_name, default_value, items,
                                                title=field_name, can_reset=False, complex_var_name=True)
    parameter_row_init_mock.assert_called_once_with(instance, action_core_mock, field_name, required)

    return instance


if __name__ == '__main__':
    unittest.main()
