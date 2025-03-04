"""
The module for the Home Assistant customization window.
"""

from enum import Enum
from typing import Callable, List, Dict

from gi.repository.Gdk import RGBA
from gi.repository.Gtk import Align, Box, Button, CellRendererText, ComboBox, CssProvider, Entry, \
    Grid, Label, ListStore, Window, ColorButton, SpinButton, CheckButton

from de_gensyn_HomeAssistantPlugin import const

CSS = b"""
combo.error {
    background-color: #ffcccc; /* Light red */
}
"""
STYLE_PROVIDER = CssProvider()
STYLE_PROVIDER.load_from_data(CSS)


def _create_label(label: str):
    result = Label(label=label)
    result.set_halign(Align.START)
    return result


class CustomizationWindow(Window):
    """
    Window to customize icons and colors.
    """
    callback: Callable

    class Customization(Enum):
        """
        Enum to control window layout and functionality.
        """
        ICON = "icon"
        TEXT = "text"

    def __init__(self, customization: Customization, lm, attributes: List, callback: Callable,
                 icons: List = None, current: Dict = None, index: int = None):
        # Create a new modal window
        super().__init__()
        self.callback = callback
        self.icons = icons
        self.lm = lm
        self.index = index
        self.customization = customization

        self.set_title(lm.get(const.LABEL_CUSTOMIZATION_TITLE))
        self.set_modal(True)

        label_attribute = _create_label(lm.get(const.LABEL_CUSTOMIZATION_ATTRIBUTE))
        label_operator = _create_label(lm.get(const.LABEL_CUSTOMIZATION_OPERATOR))
        label_value = _create_label(lm.get(const.LABEL_CUSTOMIZATION_VALUE))
        label_if = _create_label(lm.get(const.LABEL_CUSTOMIZATION_IF))

        self.combo_attribute = self._create_combo_attribute(attributes)
        self.combo_operator = self._create_combo_operator()

        self.entry_value = self._create_entry()

        cancel_button = Button(label=lm.get(const.LABEL_CUSTOMIZATION_CANCEL))
        cancel_button.connect(const.CONNECT_CLICKED, self._on_cancel_button)

        add_button = Button(label=lm.get(const.LABEL_CUSTOMIZATION_ADD) if not current else lm.get(
            const.LABEL_CUSTOMIZATION_UPDATE))
        add_button.connect(const.CONNECT_CLICKED, self._on_add_button)

        self._set_margins(
            [label_attribute, label_operator, label_value, label_if,
             self.combo_attribute,
             self.combo_operator, self.entry_value, cancel_button,
             add_button])
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

        if self.customization == CustomizationWindow.Customization.ICON:
            self._add_icon_fields(lm)

        self._set_current_values(current)

        box_buttons = Box()
        box_buttons.append(cancel_button)
        box_buttons.append(add_button)
        box_buttons.set_halign(Align.END)

        grid = Grid()
        grid.attach(self.grid_fields, 0, 0, 1, 1)
        grid.attach(box_buttons, 0, 1, 1, 1)

        self.set_child(grid)

    def _add_icon_fields(self, lm):
        self.check_icon = CheckButton()
        self.check_icon.connect(const.CONNECT_TOGGLED, self._on_widget_changed)

        self.check_color = CheckButton()
        self.check_color.connect(const.CONNECT_TOGGLED, self._on_widget_changed)

        self.check_scale = CheckButton()
        self.check_scale.connect(const.CONNECT_TOGGLED, self._on_widget_changed)

        self.check_opacity = CheckButton()
        self.check_opacity.connect(const.CONNECT_TOGGLED, self._on_widget_changed)

        label_icon = _create_label(lm.get(const.LABEL_ICON_ICON))
        label_color = _create_label(lm.get(const.LABEL_ICON_COLOR))
        label_scale = _create_label(lm.get(const.LABEL_ICON_SCALE))
        label_opacity = _create_label(lm.get(const.LABEL_ICON_OPACITY))

        self.entry_icon = self._create_entry()
        self.entry_icon.connect(const.CONNECT_ACTIVATE, self._on_widget_changed)

        self.button_color = ColorButton(use_alpha=False)

        self.spin_scale = SpinButton.new_with_range(1, 100, 1)

        self.spin_opacity = SpinButton.new_with_range(1, 100, 1)

        self._set_margins(
            [self.check_icon, self.check_color, self.check_scale, self.check_opacity, label_icon,
             label_color, label_scale, label_opacity, self.entry_icon, self.button_color,
             self.spin_scale, self.spin_opacity])

        self.grid_fields.attach(self.check_icon, 2, 2, 1, 1)
        self.grid_fields.attach(label_icon, 3, 2, 1, 1)
        self.grid_fields.attach(self.entry_icon, 4, 2, 1, 1)

        self.grid_fields.attach(self.check_color, 2, 3, 1, 1)
        self.grid_fields.attach(label_color, 3, 3, 1, 1)
        self.grid_fields.attach(self.button_color, 4, 3, 1, 1)

        self.grid_fields.attach(self.check_scale, 2, 4, 1, 1)
        self.grid_fields.attach(label_scale, 3, 4, 1, 1)
        self.grid_fields.attach(self.spin_scale, 4, 4, 1, 1)

        self.grid_fields.attach(self.check_opacity, 2, 5, 1, 1)
        self.grid_fields.attach(label_opacity, 3, 5, 1, 1)
        self.grid_fields.attach(self.spin_opacity, 4, 5, 1, 1)

    def _set_default_values(self):
        if self.customization == CustomizationWindow.Customization.ICON:
            rgba_list = const.DEFAULT_ICON_COLOR
            rgba = RGBA(use_alpha=False)
            rgba.red = rgba_list[0]
            rgba.green = rgba_list[1]

            rgba.blue = rgba_list[2]
            rgba.alpha = 1
            self.button_color.set_rgba(rgba)

            self.spin_scale.set_value(const.DEFAULT_ICON_SCALE)
            self.spin_opacity.set_value(const.DEFAULT_ICON_OPACITY)

    def _set_current_values(self, current: Dict):
        self._set_default_values()

        if not current:
            return

        for i in range(len(self.combo_attribute.get_model())):
            if self.combo_attribute.get_model()[i][0] == current[const.CUSTOM_ICON_ATTRIBUTE]:
                self.combo_attribute.set_active(i)
                break

        for i in range(len(self.combo_operator.get_model())):
            if self.combo_operator.get_model()[i][0] == current[const.CUSTOM_ICON_OPERATOR]:
                self.combo_operator.set_active(i)
                break

        self.entry_value.set_text(current[const.CUSTOM_ICON_VALUE])

        if self.customization == CustomizationWindow.Customization.ICON:
            self.entry_icon.set_text(current.get(const.CUSTOM_ICON_ICON, const.EMPTY_STRING))
            self.check_icon.set_active(const.CUSTOM_ICON_ICON in current.keys())

            if current.get(const.CUSTOM_ICON_COLOR):
                rgba_list = current[const.CUSTOM_ICON_COLOR]
                rgba = RGBA(use_alpha=False)
                rgba.red = rgba_list[0]
                rgba.green = rgba_list[1]

                rgba.blue = rgba_list[2]
                rgba.alpha = 1
                self.button_color.set_rgba(rgba)
            self.check_color.set_active(const.CUSTOM_ICON_COLOR in current.keys())

            self.spin_scale.set_value(
                current.get(const.CUSTOM_ICON_SCALE, const.DEFAULT_ICON_SCALE))
            self.check_scale.set_active(const.CUSTOM_ICON_SCALE in current.keys())

            self.spin_opacity.set_value(
                current.get(const.CUSTOM_ICON_OPACITY, const.DEFAULT_ICON_OPACITY))
            self.check_opacity.set_active(const.CUSTOM_ICON_OPACITY in current.keys())

    def _set_margins(self, elements: List) -> None:
        for element in elements:
            element.set_margin_top(3)
            element.set_margin_bottom(3)
            element.set_margin_start(3)
            element.set_margin_end(3)

    def _create_combo_attribute(self, attributes: List) -> ComboBox:
        combo = ComboBox()

        model = ListStore(str)
        for option in attributes:
            model.append([option])

        combo.set_model(model)

        renderer = CellRendererText()

        # Pack the renderer into the ComboBox
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        combo.connect(const.CONNECT_CHANGED, self._on_widget_changed)

        return combo

    def _create_combo_operator(self) -> ComboBox:
        combo = ComboBox()

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
        combo.connect(const.CONNECT_CHANGED, self._on_widget_changed)

        return combo

    def _create_entry(self):
        entry = Entry()
        entry.set_size_request(200, -1)
        entry.connect(const.CONNECT_CHANGED, self._on_widget_changed)
        entry.connect(const.CONNECT_ACTIVATE, self._on_add_button)
        return entry

    def _on_cancel_button(self, _):
        self.destroy()

    def _on_add_button(self, _):
        if self.combo_attribute.get_active() < 0:
            self.combo_attribute.get_style_context().add_class(const.ERROR)
            return

        if self.combo_operator.get_active() < 0:
            self.combo_operator.get_style_context().add_class(const.ERROR)
            return

        if not self.entry_value.get_text():
            self.entry_value.get_style_context().add_class(const.ERROR)
            return

        if self.customization == CustomizationWindow.Customization.ICON:
            if self.check_icon.get_active():
                icon = self.entry_icon.get_text()

                if icon.startswith("mdi:"):
                    icon = icon[4:]

                if self.combo_operator.get_model()[self.combo_operator.get_active()][0] in (
                        "<", "<=", ">", ">="):
                    # expecting a number in value
                    try:
                        float(self.entry_value.get_text())
                    except ValueError:
                        self.combo_operator.get_style_context().add_class(const.ERROR)
                        self.entry_value.get_style_context().add_class(const.ERROR)
                        return

                if icon not in self.icons:
                    self.entry_icon.get_style_context().add_class(const.ERROR)
                    return

            if (not self.check_icon.get_active() and not self.check_color.get_active() and not
            self.check_scale.get_active() and not self.check_opacity.get_active()):
                self.check_icon.get_style_context().add_class(const.ERROR)
                self.check_color.get_style_context().add_class(const.ERROR)
                self.check_scale.get_style_context().add_class(const.ERROR)
                self.check_opacity.get_style_context().add_class(const.ERROR)
                return

            icon = self.entry_icon.get_text() if self.check_icon.get_active() else None
            color = self.button_color.get_rgba() if self.check_color.get_active() else None
            color_list = [color.red, color.green, color.blue] if color else None
            scale = self.spin_scale.get_value() if self.check_scale.get_active() else None
            opacity = self.spin_opacity.get_value() if self.check_opacity.get_active() else None

            self.callback(
                attribute=self.combo_attribute.get_model()[self.combo_attribute.get_active()][0],
                operator=self.combo_operator.get_model()[self.combo_operator.get_active()][0],
                value=self.entry_value.get_text(), icon=icon, color=color_list, scale=scale,
                opacity=opacity, index=self.index)

        self.destroy()

    def _on_widget_changed(self, _):
        self.combo_attribute.get_style_context().remove_class(const.ERROR)
        self.combo_operator.get_style_context().remove_class(const.ERROR)
        self.entry_value.get_style_context().remove_class(const.ERROR)

        if self.customization == CustomizationWindow.Customization.ICON:
            self.entry_icon.get_style_context().remove_class(const.ERROR)
            self.check_icon.get_style_context().remove_class(const.ERROR)
            self.check_color.get_style_context().remove_class(const.ERROR)
            self.check_scale.get_style_context().remove_class(const.ERROR)
            self.check_opacity.get_style_context().remove_class(const.ERROR)
