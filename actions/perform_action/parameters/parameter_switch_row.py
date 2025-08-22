"""Module for the ParameterSwitchRow."""
from GtkHelper.GenerativeUI.SwitchRow import SwitchRow

from de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_row import ParameterRow


class ParameterSwitchRow(ParameterRow, SwitchRow):
    """SwitchRow to display action call parameters with a check button."""

    def __init__(self, action_core, var_name: str, field_name: str, default_value: bool, required: bool):
        SwitchRow.__init__(self, action_core, var_name, default_value, title=field_name,
                           can_reset=False, complex_var_name=True)
        ParameterRow.__init__(self, action_core, field_name, required)

        self.widget.add_prefix(self.check)

    def get_parameter_value(self) -> bool:
        """
        Get the value of the row.
        :return: the value
        """
        return self.get_active()

    def set_value(self, value: bool) -> None:
        """
        Set the value for the row.
        :param value: the new value
        """
        if self.check.get_active():
            SwitchRow.set_value(self, value)

    def _value_changed(self, switch, _) -> None:
        if not self.required:
            self.check.set_active(True)
        SwitchRow._value_changed(self, switch, _)
        ParameterRow._on_change(self)
