"""
Module for the ParameterSwitchRow.
"""
from GtkHelper import GenerativeUI
from de_gensyn_HomeAssistantPlugin import const

import gi
gi.require_version("Gtk", "4.0")
from gi.repository.Gtk import CheckButton

class ParameterSwitchRow(GenerativeUI.SwitchRow.SwitchRow):
    """
    SwitchRow to display service call parameters with a check button.
    """
    def __init__(self, action_core, var_name: str, field_name: str, default_value: bool):
        super().__init__(action_core, var_name, default_value, title=field_name, can_reset=False, complex_var_name=True)

        self.field_name = field_name

        self.check = CheckButton()
        is_active = self.field_name in self.action_core.settings[const.SETTING_SERVICE][const.SETTING_PARAMETERS]
        self.check.set_active(is_active)
        self.check.connect(const.CONNECT_TOGGLED, self._on_change_check)
        self.widget.add_prefix(self.check)

    def set_value(self, value: bool) -> None:
        if self.check.get_active():
            super().set_value(value)

    def _on_change_check(self, _) -> None:
        if self.check.get_active():
            self.action_core.settings.set_service_parameter(self.field_name, self.get_active())
        else:
            self.action_core.settings.remove_service_parameter(self.field_name)

    def _value_changed(self, switch, _) -> None:
        self.check.set_active(True)
        super()._value_changed(switch, _)
