"""
Module for helper functions.
"""
from typing import List, Tuple

import gi
from gi.repository.Gdk import RGBA

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Adw import ComboRow


def set_value_in_combo(combo: ComboRow, value: str):
    """
    Select the entry in the combo row corresponding to the index of the model equalling the given
    value. Does nothing if the value does not exist in the model.
    """
    if not value:
        return

    for i in range(combo.get_model().get_n_items()):
        if combo.get_model().get_string(i) == value:
            combo.set_selected(i)
            return


def convert_color_list_to_rgba(color: List) -> RGBA:
    """
    Converts a list with RGB values to an RGBA object.
    The alpha value is always set to 1.
    :param color: the color list to convert
    :return: the RGBA color
    """
    rgba = RGBA()
    rgba.red = color[0]
    rgba.green = color[1]
    rgba.blue = color[2]
    rgba.alpha = 1
    return rgba

def convert_color_list_to_hex(color: Tuple[int, int, int, int]) -> str:
    """
    Converts a tuple with RGBA values to a hex string representation.
    :param color: the color to convert
    :return: the color as a hex string
    """
    return f'#{int(color[0]):02X}{int(color[1]):02X}{int(color[2]):02X}'
