"""
Module for helper functions.
"""
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import StringList
from gi.repository.Adw import ComboRow


def set_value_in_combo(combo: ComboRow, model: StringList, value: str):
    """
    Select the entry in the combo row corresponding to the index of the model equalling the given
    value. Does nothing if the value does not exist in the model.
    """
    if not value:
        return

    for i in range(model.get_n_items()):
        if model.get_string(i) == value:
            combo.set_selected(i)
            return
