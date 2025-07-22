"""Module for the ParameterRow."""
from typing import  Any

from gi.repository.Gtk import CheckButton

from de_gensyn_HomeAssistantPlugin import const as base_const


class ParameterRow:
    """Row to display action call parameters with a check button."""
    def __init__(self, action_core, field_name: str):
        self.action = action_core
        self.field_name = field_name

        self.check = CheckButton()
        is_active = self.field_name in self.action.settings.get_action_parameters()
        self.check.set_active(is_active)
        self.check.connect(base_const.CONNECT_TOGGLED, self._on_change_check)

    def get_parameter_value(self) -> Any:
        """
        Get the value of the row. Must be implemented in a subclass.
        :return: the value
        """
        pass


    def set_value(self, value: Any) -> None:
        """
        Set the value for the row. Must be implemented in a subclass.
        :param value: the new value
        """
        pass

    def _on_change_check(self, _) -> None:
        if self.check.get_active():
            self.action.settings.set_action_parameter(self.field_name, self.get_parameter_value())
        else:
            self.action.settings.remove_action_parameter(self.field_name)
