"""Module for the ParameterScaleRow."""

from GtkHelper.GenerativeUI.ScaleRow import ScaleRow
from de_gensyn_HomeAssistantPlugin.actions.ActionAction.action_parameters.parameter_row import ParameterRow


class ParameterScaleRow(ParameterRow, ScaleRow):
    """ScaleRow to display action call parameters with a check button."""

    def __init__(self, action_core, var_name: str, field_name: str, default_value: bool, min_value, max_value, step):
        digits = 0
        if "." in str(step):
            digits = len(str(step).split(".")[1])

        ParameterRow.__init__(self, action_core, field_name)
        ScaleRow.__init__(self, action_core, var_name, default_value, title=field_name, min=min_value, max=max_value,
                          step=step, digits=digits, can_reset=False, complex_var_name=True)

        self.widget.add_prefix(self.check)

    def get_parameter_value(self) -> float:
        """
        Get the value of the row.
        :return: the value
        """
        return self.get_number()

    def set_value(self, value: float | int) -> None:
        """
        Set the value for the row.
        :param value: the new value
        """
        if self.check.get_active():
            ScaleRow.set_value(self, value)

    def _value_changed(self, scale) -> None:
        self.check.set_active(True)
        ScaleRow._value_changed(self, scale)
