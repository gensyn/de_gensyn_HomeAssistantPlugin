"""
The module for the Home Assistant customization window.
"""

from enum import Enum
from typing import Callable, List, Dict

from gi.repository.Gtk import Align, Box, Button, CellRendererText, ComboBox, CssProvider, Entry, \
    Grid, Label, ListStore, Window

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
        ICON_COLOR = "icon color"
        ICON = "icon"

    def __init__(self, customization: Customization, lm, attributes: List, callback: Callable,
                 icons: List = None, current: Dict = None, index: int = None):
        # Create a new modal window
        super().__init__()
        self.callback = callback
        self.icons = icons
        self.lm = lm
        self.index = index

        self.set_title(lm.get(const.LABEL_CUSTOMIZATION_TITLE))
        self.set_modal(True)

        label_attribute = _create_label(lm.get(const.LABEL_CUSTOMIZATION_ATTRIBUTE))
        label_operator = _create_label(lm.get(const.LABEL_CUSTOMIZATION_OPERATOR))
        label_value = _create_label(lm.get(const.LABEL_CUSTOMIZATION_VALUE))
        label_icon = _create_label(lm.get(const.LABEL_CUSTOMIZATION_ICON))
        label_if = _create_label(lm.get(const.LABEL_CUSTOMIZATION_IF))
        label_then = _create_label(lm.get(const.LABEL_CUSTOMIZATION_THEN))

        self.combo_attribute = self._create_combo_attribute(attributes)
        self.combo_operator = self._create_combo_operator()

        self.entry_value = self._create_entry()


        self.entry_icon = self._create_entry()

        cancel_button = Button(label=lm.get(const.LABEL_CUSTOMIZATION_CANCEL))
        cancel_button.connect(const.CONNECT_CLICKED, self._on_cancel_button)

        add_button = Button(label=lm.get(const.LABEL_CUSTOMIZATION_ADD) if not current else lm.get(
            const.LABEL_CUSTOMIZATION_UPDATE))
        add_button.connect(const.CONNECT_CLICKED, self._on_add_button)

        self._set_margins(
            [label_attribute, label_operator, label_value, label_icon, label_if,
             self.combo_attribute,
             self.combo_operator, self.entry_value, label_then, self.entry_icon, cancel_button,
             add_button])
        cancel_button.set_margin_bottom(5)
        add_button.set_margin_bottom(5)
        add_button.set_margin_end(5)
        label_if.set_margin_start(5)
        self.entry_icon.set_margin_end(5)

        self._set_current_values(current)

        grid_fields = Grid()
        grid_fields.attach(label_attribute, 1, 0, 1, 1)
        grid_fields.attach(label_operator, 2, 0, 1, 1)
        grid_fields.attach(label_value, 3, 0, 1, 1)
        grid_fields.attach(label_icon, 5, 0, 1, 1)
        grid_fields.attach(label_if, 0, 1, 1, 1)
        grid_fields.attach(self.combo_attribute, 1, 1, 1, 1)
        grid_fields.attach(self.combo_operator, 2, 1, 1, 1)
        grid_fields.attach(self.entry_value, 3, 1, 1, 1)
        grid_fields.attach(label_then, 4, 1, 1, 1)
        grid_fields.attach(self.entry_icon, 5, 1, 1, 1)

        box_buttons = Box()
        box_buttons.append(cancel_button)
        box_buttons.append(add_button)
        box_buttons.set_halign(Align.END)

        grid = Grid()
        grid.attach(grid_fields, 0, 0, 1, 1)
        grid.attach(box_buttons, 0, 1, 1, 1)

        self.set_child(grid)

    def _set_current_values(self, current: Dict):
        if not current:
            return

        for i in range(len(self.combo_attribute.get_model())):
            if self.combo_attribute.get_model()[i][0] == current["attribute"]:
                self.combo_attribute.set_active(i)
                break

        for i in range(len(self.combo_operator.get_model())):
            if self.combo_operator.get_model()[i][0] == current["operator"]:
                self.combo_operator.set_active(i)
                break

        self.entry_value.set_text(current["value"])
        self.entry_icon.set_text(current["icon"])

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

        self.callback(
            attribute=self.combo_attribute.get_model()[self.combo_attribute.get_active()][0],
            operator=self.combo_operator.get_model()[self.combo_operator.get_active()][0],
            value=self.entry_value.get_text(), target=self.entry_icon.get_text(), index=self.index)

        self.destroy()

    def _on_widget_changed(self, _):
        self.combo_attribute.get_style_context().remove_class(const.ERROR)
        self.combo_operator.get_style_context().remove_class(const.ERROR)
        self.entry_value.get_style_context().remove_class(const.ERROR)
        self.entry_icon.get_style_context().remove_class(const.ERROR)
