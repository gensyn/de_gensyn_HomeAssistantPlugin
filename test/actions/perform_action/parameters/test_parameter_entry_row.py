import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row import ParameterEntryRow


class TestParameterEntryRow(unittest.TestCase):

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow.__init__')
    def test_init(self, parameter_row_init_mock, entry_row_init_mock):
        create_instance(entry_row_init_mock, parameter_row_init_mock, False)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.get_text')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow.__init__')
    def test_get_parameter_value(self, parameter_row_init_mock, entry_row_init_mock, get_text_mock):
        instance = create_instance(entry_row_init_mock, parameter_row_init_mock, False)
        get_text_mock.return_value = "current_text"
        result = instance.get_parameter_value()

        self.assertEqual(result, "current_text")

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow.__init__')
    def test_set_value_check_not_active(self, parameter_row_init_mock, entry_row_init_mock, entry_row_set_value_mock):
        instance = create_instance(entry_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=False)
        instance.set_value("new_value")

        instance.check.get_active.assert_called_once()
        entry_row_set_value_mock.assert_not_called()

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow.__init__')
    def test_set_value_check_active(self, parameter_row_init_mock, entry_row_init_mock, entry_row_set_value_mock):
        instance = create_instance(entry_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=True)
        instance.set_value("new_value")

        instance.check.get_active.assert_called_once()
        entry_row_set_value_mock.assert_called_once_with(instance, "new_value")

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow.__init__')
    def test_value_changed_required(self, parameter_row_init_mock, parameter_row_on_change_mock, entry_row_init_mock,
                                    entry_row_value_changed_mock):
        instance = create_instance(entry_row_init_mock, parameter_row_init_mock, True)
        instance.check.set_active = Mock()
        instance._value_changed(instance)

        instance.check.set_active.assert_not_called()
        entry_row_value_changed_mock.assert_called_once_with(instance, instance)
        parameter_row_on_change_mock.assert_called_once_with(instance)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.get_text')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.EntryRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row.ParameterRow.__init__')
    def test_value_changed_not_required(self, parameter_row_init_mock, parameter_row_on_change_mock,
                                        entry_row_init_mock, entry_row_value_changed_mock, get_text_mock):
        get_text_mock.return_value = "False"
        instance = create_instance(entry_row_init_mock, parameter_row_init_mock, False)
        instance.check.set_active = Mock()
        instance._value_changed(instance)

        get_text_mock.assert_called_once_with()
        instance.check.set_active.assert_called_once_with(True)
        entry_row_value_changed_mock.assert_called_once_with(instance, instance)
        parameter_row_on_change_mock.assert_called_once_with(instance)


def create_instance(entry_row_init_mock, parameter_row_init_mock, required) -> ParameterEntryRow:
    action_core_mock = Mock()
    var_name = "test_var"
    field_name = "test_field"
    default_value = "default_value"

    def add_instance_attributes(entry_row, *_, **__):
        entry_row.widget = Mock()
        entry_row.check = Mock()
        entry_row.required = required

    entry_row_init_mock.side_effect = add_instance_attributes

    instance = ParameterEntryRow(action_core_mock, var_name, field_name, default_value, required)

    entry_row_init_mock.assert_called_once_with(instance, action_core_mock, var_name, default_value,
                                                title=field_name, can_reset=False, complex_var_name=True)
    parameter_row_init_mock.assert_called_once_with(instance, action_core_mock, field_name, required)

    return instance

