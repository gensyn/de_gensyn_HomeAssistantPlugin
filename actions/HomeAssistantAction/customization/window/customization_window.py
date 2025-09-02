"""
The module for the Home Assistant customization window.
"""
from functools import partial
from typing import Callable, List

import gi
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.customization import Customization

gi.require_version("Gtk", "4.0")
from gi.repository.Gtk import Align, Box, Button, CellRendererText, ComboBox, CssProvider, Entry, \
    Grid, Label, ListStore, Window, ColorButton, CheckButton, Scale, Orientation, Switch

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import icon_helper

CSS = b"""
combo.error {
    background-color: #ffcccc; /* Light red */
}
"""
STYLE_PROVIDER = CssProvider()
STYLE_PROVIDER.load_from_data(CSS)


class CustomizationWindow(Window):
    """
    Base for customization windows
    """
    callback: Callable

    connect_rows: List = []
    default_margin = 3

    def __init__(self, customization_type: str, lm, attributes: List, callback: Callable,
                 current: Customization = None, index: int = None):
        super().__init__()
        self.callback = callback
        self.icons: List[str] = list(icon_helper.MDI_ICONS)
        self.lm = lm
        self.index: int = index
        self.attributes: List[str] = attributes
        self.current: Customization = current
        self.customization_type: str = customization_type

        self.set_modal(True)

        label_attribute = self._create_label(lm.get(const.LABEL_CUSTOMIZATION_ATTRIBUTE))
        label_operator = self._create_label(lm.get(const.LABEL_CUSTOMIZATION_OPERATOR))
        label_value = self._create_label(lm.get(const.LABEL_CUSTOMIZATION_VALUE))
        label_if = self._create_label(lm.get(const.LABEL_CUSTOMIZATION_IF))

        self.combo_attribute = self._create_combo(self.attributes)
        self.combo_operator = self._create_combo_operator()

        self.entry_value = self._create_entry()

        cancel_button = self._create_button(lm.get(const.LABEL_CUSTOMIZATION_CANCEL))
        self.connect_rows.append(
            partial(cancel_button.connect, const.CONNECT_CLICKED, self._on_cancel_button))

        add_label = lm.get(const.LABEL_CUSTOMIZATION_ADD) if not current else lm.get(
            const.LABEL_CUSTOMIZATION_UPDATE)
        add_button = self._create_button(add_label)
        self.connect_rows.append(
            partial(add_button.connect, const.CONNECT_CLICKED, self._on_add_button))

        label_attribute.set_margin_top(15)
        label_operator.set_margin_top(15)
        label_value.set_margin_top(15)
        cancel_button.set_margin_bottom(15)
        add_button.set_margin_bottom(15)
        add_button.set_margin_end(15)
        label_if.set_margin_start(15)
        label_if.set_margin_bottom(30)
        self.combo_attribute.set_margin_bottom(30)
        self.combo_operator.set_margin_bottom(30)
        self.entry_value.set_margin_end(15)
        self.entry_value.set_margin_bottom(30)

        self.grid_fields = Grid()
        self.grid_fields.attach(label_attribute, 1, 0, 1, 1)
        self.grid_fields.attach(label_operator, 4, 0, 1, 1)
        self.grid_fields.attach(label_value, 5, 0, 1, 1)
        self.grid_fields.attach(label_if, 0, 1, 1, 1)
        self.grid_fields.attach(self.combo_attribute, 1, 1, 3, 1)
        self.grid_fields.attach(self.combo_operator, 4, 1, 1, 1)
        self.grid_fields.attach(self.entry_value, 5, 1, 1, 1)

        box_buttons = Box()
        box_buttons.append(cancel_button)
        box_buttons.append(add_button)
        box_buttons.set_halign(Align.END)

        grid = Grid()
        grid.attach(self.grid_fields, 0, 0, 1, 1)
        grid.attach(box_buttons, 0, 1, 1, 1)

        self.set_child(grid)

    def _after_init(self) -> None:
        self._set_default_values()
        self._set_current_values(self.current)
        self._connect_rows()

    def _set_default_values(self) -> None:
        self.combo_attribute.set_active(0)
        self.combo_operator.set_active(0)

    def _set_current_values(self, current: Customization) -> None:
        if not current:
            return

        for index, entry in enumerate(self.combo_attribute.get_model()):
            if entry[0] == current.get_attribute():
                self.combo_attribute.set_active(index)
                break

        for index, entry in enumerate(self.combo_operator.get_model()):
            if entry[0] == current.get_operator():
                self.combo_operator.set_active(index)
                break

        self.entry_value.set_text(current.get_value())

    def _create_button(self, label) -> Button:
        button = Button(label=label)
        button.set_margin_top(self.default_margin)
        button.set_margin_bottom(self.default_margin)
        button.set_margin_start(self.default_margin)
        button.set_margin_end(self.default_margin)
        return button

    def _create_combo(self, attributes: List, check: CheckButton = None) -> ComboBox:
        combo = ComboBox()
        combo.set_margin_top(self.default_margin)
        combo.set_margin_bottom(self.default_margin)
        combo.set_margin_start(self.default_margin)
        combo.set_margin_end(self.default_margin)

        model = ListStore(str)
        for option in attributes:
            model.append([option])

        combo.set_model(model)

        renderer = CellRendererText()

        # Pack the renderer into the ComboBox
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        self.connect_rows.append(
            partial(combo.connect, const.CONNECT_CHANGED, self._on_widget_changed))

        if check is not None:
            self.connect_rows.append(partial(combo.connect, const.CONNECT_CHANGED,
                                             lambda _: check.set_active(combo.get_active() >= 0)))

        return combo

    def _create_combo_operator(self) -> ComboBox:
        combo = ComboBox()
        combo.set_margin_top(self.default_margin)
        combo.set_margin_bottom(self.default_margin)
        combo.set_margin_start(self.default_margin)
        combo.set_margin_end(self.default_margin)

        model = ListStore(str, str)
        model.append(["==", self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS["=="])])
        model.append(["!=", self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS["!="])])
        model.append(["<", self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS["<"])])
        model.append(["<=", self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS["<="])])
        model.append([">", self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS[">"])])
        model.append([">=", self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS[">="])])

        combo.set_model(model)

        renderer = CellRendererText()

        # Pack the renderer into the ComboBox
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 1)
        self.connect_rows.append(
            partial(combo.connect, const.CONNECT_CHANGED, self._on_widget_changed))

        return combo

    def _create_label(self, label: str):
        label = Label(label=label)
        label.set_margin_top(self.default_margin)
        label.set_margin_bottom(self.default_margin)
        label.set_margin_start(self.default_margin)
        label.set_margin_end(self.default_margin)
        label.set_halign(Align.START)
        return label

    def _create_entry(self, check: CheckButton = None) -> Entry:
        entry = Entry()
        entry.set_margin_top(self.default_margin)
        entry.set_margin_bottom(self.default_margin)
        entry.set_margin_start(self.default_margin)
        entry.set_margin_end(15)
        self.connect_rows.append(
            partial(entry.connect, const.CONNECT_CHANGED, self._on_widget_changed))
        self.connect_rows.append(
            partial(entry.connect, const.CONNECT_ACTIVATE, self._on_add_button))
        if check is not None:
            self.connect_rows.append(partial(entry.connect, const.CONNECT_CHANGED,
                                             lambda _: check.set_active(
                                                 entry.get_text() != const.EMPTY_STRING)))
        return entry

    def _create_scale(self, min_value: int, max_value: int, step: int, check: CheckButton) -> Scale:
        scale = Scale.new_with_range(Orientation.HORIZONTAL, min_value, max_value, step)
        scale.set_margin_top(self.default_margin)
        scale.set_margin_bottom(self.default_margin)
        scale.set_margin_start(self.default_margin)
        scale.set_margin_end(self.default_margin)
        self.connect_rows.append(
            partial(scale.connect, const.CONNECT_VALUE_CHANGED, lambda _: check.set_active(True)))
        return scale

    def _create_scale_entry(self, check) -> Entry:
        entry = Entry()
        entry.set_margin_top(self.default_margin)
        entry.set_margin_bottom(self.default_margin)
        entry.set_margin_start(self.default_margin)
        entry.set_margin_end(180)
        entry.set_width_chars(4)
        entry.set_max_width_chars(4)
        self.connect_rows.append(
            partial(entry.connect, const.CONNECT_ACTIVATE, self._on_add_button))
        self.connect_rows.append(partial(entry.connect, const.CONNECT_CHANGED,
                                         lambda _: check.set_active(
                                             entry.get_text() != const.EMPTY_STRING)))
        return entry

    def _create_switch(self, check: CheckButton) -> Switch:
        switch = Switch()
        switch.set_margin_top(self.default_margin)
        switch.set_margin_bottom(self.default_margin)
        switch.set_margin_start(self.default_margin)
        switch.set_margin_end(self.default_margin)
        switch.set_halign(Align.START)
        self.connect_rows.append(partial(switch.connect, const.CONNECT_NOTIFY_ACTIVE,
                                         lambda _, __: check.set_active(True)))
        return switch

    def _create_color_button(self, check: CheckButton) -> ColorButton:
        button = ColorButton(use_alpha=False)
        button.set_margin_top(self.default_margin)
        button.set_margin_bottom(self.default_margin)
        button.set_margin_start(self.default_margin)
        button.set_margin_end(self.default_margin)
        self.connect_rows.append(partial(button.connect, const.CONNECT_NOTIFY_COLOR_SET,
                                         lambda _: check.set_active(True)))
        return button

    def _on_cancel_button(self, _):
        self.destroy()

    def _on_add_button(self, _) -> bool:
        if self.combo_attribute.get_active() < 0:
            self.combo_attribute.add_css_class(const.ERROR)
            return False

        if self.combo_operator.get_active() < 0:
            self.combo_operator.add_css_class(const.ERROR)
            return False

        if not self.entry_value.get_text():
            self.entry_value.add_css_class(const.ERROR)
            return False

        if self.combo_operator.get_active() > 1 and not self._is_number(
                self.entry_value.get_text()):
            # operator needs a number
            self.combo_operator.add_css_class(const.ERROR)
            self.entry_value.add_css_class(const.ERROR)
            return False

        return True

    def _on_widget_changed(self, _):
        self.combo_attribute.remove_css_class(const.ERROR)
        self.combo_operator.remove_css_class(const.ERROR)
        self.entry_value.remove_css_class(const.ERROR)

    def _connect_rows(self) -> None:
        """
        Connect all input fields to functions to be called on changes.
        """
        for connect in self.connect_rows:
            connect()

    def _create_check_button(self) -> CheckButton:
        check = CheckButton()
        check.set_margin_top(self.default_margin)
        check.set_margin_bottom(self.default_margin)
        check.set_margin_start(self.default_margin)
        check.set_margin_end(self.default_margin)
        self.connect_rows.append(
            partial(check.connect, const.CONNECT_TOGGLED, self._on_widget_changed))
        return check

    def _on_change_scale(self, scale, *args):
        entry: Entry = args[0]
        min_value = args[1]
        max_value = args[2]

        value = scale.get_value()
        value_in_range = min(max(value, min_value), max_value)

        if value != value_in_range:
            scale.disconnect_by_func(self._on_change_scale)
            scale.set_value(value_in_range)
            scale.connect(const.CONNECT_VALUE_CHANGED, self._on_change_scale, entry, min_value,
                          max_value)

        entry.disconnect_by_func(self._on_change_scale_entry)
        entry.set_text(str(int(value)))
        entry.connect(const.CONNECT_CHANGED, self._on_change_scale_entry, scale, min_value,
                      max_value)

    def _on_change_scale_entry(self, entry, *args):
        scale: Scale = args[0]
        min_value = args[1]
        max_value = args[2]

        text = entry.get_text()
        # remove all non-digits
        text_digits = ''.join([char for char in text if char.isdigit()])

        if not text_digits:
            text_digits = min_value

        value = int(text_digits)
        value_in_range = min(max(value, min_value), max_value)

        if text != str(value_in_range):
            entry.disconnect_by_func(self._on_change_scale_entry)
            entry.set_text(str(value_in_range))
            entry.connect(const.CONNECT_CHANGED, self._on_change_scale_entry, scale, min_value,
                          max_value)

        scale.disconnect_by_func(self._on_change_scale)
        scale.set_value(value_in_range)
        scale.connect(const.CONNECT_VALUE_CHANGED, self._on_change_scale, entry, min_value,
                      max_value)

    def _is_number(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
