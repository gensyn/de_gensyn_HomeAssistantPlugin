"""Module for the ParameterEntryRow."""
from GtkHelper.GenerativeUI.EntryRow import EntryRow

from de_gensyn_HomeAssistantPlugin.actions.perform_action.parameters.parameter_row import ParameterRow


class ParameterEntryRow(ParameterRow, EntryRow):
    """EntryRow to display action call parameters with a check button."""

    def __init__(self, action_core, var_name: str, field_name: str, default_value: str, required: bool):
        EntryRow.__init__(self, action_core, var_name, default_value, title=field_name,
                          can_reset=False, complex_var_name=True)
        ParameterRow.__init__(self, action_core, field_name, required)

        self.widget.add_prefix(self.check)

    def get_parameter_value(self) -> str:
        """
        Get the value of the row.
        :return: the value
        """
        return self.get_text()

    def set_value(self, value: str) -> None:
        """
        Set the value for the row.
        :param value: the new value
        """
        if self.check.get_active():
            EntryRow.set_value(self, value)

    def _value_changed(self, entry_row) -> None:
        if not self.required:
            self.check.set_active(bool(self.get_text()))
        EntryRow._value_changed(self, entry_row)
        ParameterRow._on_change(self)
