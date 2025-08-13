import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row import ParameterScaleRow


class TestParameterScaleRow(unittest.TestCase):

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow.__init__')
    def test_init(self, parameter_row_init_mock, scale_row_init_mock):
        create_instance(scale_row_init_mock, parameter_row_init_mock, False)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.get_number')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow.__init__')
    def test_get_parameter_value(self, parameter_row_init_mock, scale_row_init_mock, get_number_mock):
        instance = create_instance(scale_row_init_mock, parameter_row_init_mock, False)
        get_number_mock.return_value = 3.5
        result = instance.get_parameter_value()

        self.assertEqual(result, 3.5)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow.__init__')
    def test_set_value_check_not_active(self, parameter_row_init_mock, scale_row_init_mock, scale_row_set_value_mock):
        instance = create_instance(scale_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=False)
        instance.set_value(4.5)

        instance.check.get_active.assert_called_once()
        scale_row_set_value_mock.assert_not_called()

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.set_value')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow.__init__')
    def test_set_value_check_active(self, parameter_row_init_mock, scale_row_init_mock, scale_row_set_value_mock):
        instance = create_instance(scale_row_init_mock, parameter_row_init_mock, False)
        instance.check.get_active = Mock(return_value=True)
        instance.set_value(5.5)

        instance.check.get_active.assert_called_once()
        scale_row_set_value_mock.assert_called_once_with(instance, 5.5)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow.__init__')
    def test_value_changed_required(self, parameter_row_init_mock, parameter_row_on_change_mock, scale_row_init_mock,
                                    scale_row_value_changed_mock):
        instance = create_instance(scale_row_init_mock, parameter_row_init_mock, True)
        instance.check.set_active = Mock()
        instance._value_changed(instance)

        instance.check.set_active.assert_not_called()
        scale_row_value_changed_mock.assert_called_once_with(instance, instance)
        parameter_row_on_change_mock.assert_called_once_with(instance)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow._value_changed')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ScaleRow.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow._on_change')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.parameter_scale_row.ParameterRow.__init__')
    def test_value_changed_not_required(self, parameter_row_init_mock, parameter_row_on_change_mock,
                                        scale_row_init_mock, scale_row_value_changed_mock):
        instance = create_instance(scale_row_init_mock, parameter_row_init_mock, False)
        instance.check.set_active = Mock()
        instance._value_changed(instance)

        instance.check.set_active.assert_called_once_with(True)
        scale_row_value_changed_mock.assert_called_once_with(instance, instance)
        parameter_row_on_change_mock.assert_called_once_with(instance)


def create_instance(scale_row_init_mock, parameter_row_init_mock, required) -> ParameterScaleRow:
    action_core_mock = Mock()
    var_name = "test_var"
    field_name = "test_field"
    default_value = "default_value"
    scale_min = 1
    scale_max = 99
    step = 0.555

    def add_instance_attributes(scale_row, *_, **__):
        scale_row.widget = Mock()
        scale_row.check = Mock()
        scale_row.required = required

    scale_row_init_mock.side_effect = add_instance_attributes

    instance = ParameterScaleRow(action_core_mock, var_name, field_name, default_value, scale_min, scale_max, step,
                                 required)

    # expect 3 digits for 3 float places in the step value
    scale_row_init_mock.assert_called_once_with(instance, action_core_mock, var_name, default_value,
                                                title=field_name, min=scale_min, max=scale_max, step=step,
                                                digits=3, can_reset=False, complex_var_name=True)
    parameter_row_init_mock.assert_called_once_with(instance, action_core_mock, field_name, required)

    return instance


if __name__ == '__main__':
    unittest.main()
