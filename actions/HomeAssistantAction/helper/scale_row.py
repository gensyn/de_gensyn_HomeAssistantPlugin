"""
Module for helper functions.
"""
import gi

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import const

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.GObject import SignalFlags
from gi.repository.Gtk import Box, Entry, Label, Orientation, Scale
from gi.repository.Adw import PreferencesRow


class ScaleRow(PreferencesRow):
    """
    A row with a scale and an entry to pick numbers.
    """
    __gtype_name__ = "ScaleRow"
    __gsignals__ = {
        const.CONNECT_VALUE_CHANGED: (SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, title: str, min_value: int, max_value: int, step: int):
        super().__init__()

        self.min_value = min_value
        self.max_value = max_value

        label: Label = Label(label=title)
        label.set_size_request(60, 0)
        label.set_xalign(0.0)

        self.entry: Entry = Entry()
        self.entry.set_max_width_chars(5)
        self.entry.set_width_chars(5)
        self.entry.set_margin_top(10)
        self.entry.set_margin_bottom(10)

        self.scale: Scale = Scale.new_with_range(Orientation.HORIZONTAL, min_value, max_value, step)
        self.scale.set_hexpand(True)

        self.box: Box = Box(orientation=Orientation.HORIZONTAL)
        self.box.set_margin_start(10)
        self.box.set_margin_end(10)
        self.box.set_homogeneous(False)

        self.box.append(label)
        self.box.append(self.scale)
        self.box.append(self.entry)

        self.set_child(self.box)
        self.set_size_request(-1, 55)
        self._connect_signals()

    def add_prefix(self, widget):
        """
        Adds the widget to the start of the row.
        """
        widget.set_margin_start(2)
        widget.set_margin_end(12)
        self.box.insert_child_after(widget, None)

    def get_value(self) -> int:
        """
        Gets the current value of the scale.
        """
        return int(self.scale.get_value())

    def set_value(self, value: int) -> None:
        """
        Sets the value of the scale.
        """
        self._disconnect_signals()
        self.scale.set_value(value)
        self.entry.set_text(str(value))
        self._connect_signals()

    def _on_change_scale(self, _) -> None:
        self._disconnect_signals()

        value = self.scale.get_value()
        value_in_range = min(max(value, self.min_value), self.max_value)

        if value != value_in_range:
            self.scale.set_value(value_in_range)

        self.entry.set_text(str(int(value)))

        self.emit(const.CONNECT_VALUE_CHANGED, self)
        self._connect_signals()

    def _on_change_entry(self, _):
        self._disconnect_signals()

        text = self.entry.get_text()
        # remove all non-digits
        text_digits = ''.join([char for char in text if char.isdigit()])

        if not text_digits:
            text_digits = self.min_value

        value = int(text_digits)
        value_in_range = min(max(value, self.min_value), self.max_value)

        if text != str(value_in_range):
            self.entry.set_text(str(value_in_range))

        self.scale.set_value(value_in_range)

        self.emit(const.CONNECT_VALUE_CHANGED, self)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.scale.connect(const.CONNECT_VALUE_CHANGED, self._on_change_scale)
        self.entry.connect(const.CONNECT_CHANGED, self._on_change_entry)

    def _disconnect_signals(self) -> None:
        self.scale.disconnect_by_func(self._on_change_scale)
        self.entry.disconnect_by_func(self._on_change_entry)
