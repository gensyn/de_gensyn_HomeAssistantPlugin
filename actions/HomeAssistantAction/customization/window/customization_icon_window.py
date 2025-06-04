"""
The module for the Home Assistant customization icon window.
"""

from functools import partial
from typing import Callable, List

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.icon_customization import IconCustomization
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.window.customization_window \
    import CustomizationWindow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import helper


class CustomizationIconWindow(CustomizationWindow):
    """
    Window to customize icons.
    """

    def __init__(self, lm, attributes: List, callback: Callable,
                 current: IconCustomization = None, index: int = None):
        super().__init__(const.CUSTOMIZATION_TYPE_ICON, lm, attributes, callback, current, index)

        self.set_title(lm.get(const.LABEL_CUSTOMIZATION_ICON_TITLE))

        self.check_icon = self._create_check_button()
        self.check_color = self._create_check_button()
        self.check_scale = self._create_check_button()
        self.check_opacity = self._create_check_button()

        label_icon = self._create_label(self.lm.get(const.LABEL_ICON_ICON))
        label_color = self._create_label(self.lm.get(const.LABEL_ICON_COLOR))
        label_scale = self._create_label(self.lm.get(const.LABEL_ICON_SCALE))
        label_opacity = self._create_label(self.lm.get(const.LABEL_ICON_OPACITY))

        self.entry_icon = self._create_entry(self.check_icon)
        self.entry_icon.set_margin_end(self.default_margin)
        self.connect_rows.append(
            partial(self.entry_icon.connect, const.CONNECT_ACTIVATE, self._on_widget_changed))

        self.button_color = self._create_color_button(self.check_color)

        self.scale_scale = self._create_scale(const.ICON_MIN_SCALE, const.ICON_MAX_SCALE, 1,
                                              self.check_scale)

        self.entry_scale = self._create_scale_entry(self.check_scale)
        self.entry_scale.set_hexpand(True)

        self.connect_rows.append(
            partial(self.scale_scale.connect, const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.entry_scale, const.ICON_MIN_SCALE,
                    const.ICON_MAX_SCALE))
        self.connect_rows.append(
            partial(self.entry_scale.connect, const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.scale_scale, const.ICON_MIN_SCALE,
                    const.ICON_MAX_SCALE))

        self.scale_opacity = self._create_scale(const.ICON_MIN_OPACITY, const.ICON_MAX_OPACITY, 1,
                                                self.check_opacity)

        self.entry_opacity = self._create_scale_entry(self.check_opacity)
        self.entry_opacity.set_hexpand(True)

        self.connect_rows.append(
            partial(self.scale_opacity.connect, const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.entry_opacity, const.ICON_MIN_OPACITY,
                    const.ICON_MAX_OPACITY))
        self.connect_rows.append(
            partial(self.entry_opacity.connect, const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.scale_opacity, const.ICON_MIN_OPACITY,
                    const.ICON_MAX_OPACITY))

        self.grid_fields.attach(self.check_icon, 2, 2, 1, 1)
        self.grid_fields.attach(label_icon, 3, 2, 1, 1)
        self.grid_fields.attach(self.entry_icon, 4, 2, 1, 1)

        self.grid_fields.attach(self.check_color, 2, 3, 1, 1)
        self.grid_fields.attach(label_color, 3, 3, 1, 1)
        self.grid_fields.attach(self.button_color, 4, 3, 1, 1)

        self.grid_fields.attach(self.check_scale, 2, 4, 1, 1)
        self.grid_fields.attach(label_scale, 3, 4, 1, 1)
        self.grid_fields.attach(self.scale_scale, 4, 4, 1, 1)
        self.grid_fields.attach(self.entry_scale, 5, 4, 1, 1)

        self.grid_fields.attach(self.check_opacity, 2, 5, 1, 1)
        self.grid_fields.attach(label_opacity, 3, 5, 1, 1)
        self.grid_fields.attach(self.scale_opacity, 4, 5, 1, 1)
        self.grid_fields.attach(self.entry_opacity, 5, 5, 1, 1)

        self._after_init()

    def _set_default_values(self) -> None:
        super()._set_default_values()

        rgba = helper.convert_color_list_to_rgba(const.DEFAULT_ICON_COLOR)
        self.button_color.set_rgba(rgba)

        self.scale_scale.set_value(const.DEFAULT_ICON_SCALE)
        self.entry_scale.set_text(str(const.DEFAULT_ICON_SCALE))

        self.scale_opacity.set_value(const.DEFAULT_ICON_OPACITY)
        self.entry_opacity.set_text(str(const.DEFAULT_ICON_OPACITY))

    def _set_current_values(self, current: IconCustomization) -> None:
        if not current:
            return

        super()._set_current_values(current)

        self.entry_icon.set_text(current.get_icon() or const.EMPTY_STRING)
        self.check_icon.set_active(current.get_icon() is not None)

        if current.get_color():
            rgba = helper.convert_color_list_to_rgba(current.get_color())
            self.button_color.set_rgba(rgba)
        self.check_color.set_active(current.get_color() is not None)

        self.scale_scale.set_value(
            current.get_scale() or const.DEFAULT_ICON_SCALE)
        self.check_scale.set_active(current.get_scale() is not None)
        self.entry_scale.set_text(
            str(int(current.get_scale() or const.DEFAULT_ICON_SCALE)))

        self.scale_opacity.set_value(
            current.get_opacity() or const.DEFAULT_ICON_OPACITY)
        self.check_opacity.set_active(current.get_opacity() is not None)
        self.entry_opacity.set_text(
            str(int(current.get_opacity() or const.DEFAULT_ICON_OPACITY)))

    def _on_add_button(self, _):
        if not super()._on_add_button(_):
            return

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
        color_list = helper.convert_rgba_to_color_list(color) if color else None
        scale = int(self.scale_scale.get_value()) if self.check_scale.get_active() else None
        opacity = int(
            self.scale_opacity.get_value()) if self.check_opacity.get_active() else None

        self.callback(
            attribute=self.combo_attribute.get_model()[self.combo_attribute.get_active()][0],
            operator=self.combo_operator.get_model()[self.combo_operator.get_active()][0],
            value=self.entry_value.get_text(), icon=icon, color=color_list, scale=scale,
            opacity=opacity, index=self.index)

        self.destroy()

    def _on_widget_changed(self, _):
        super()._on_widget_changed(_)

        self.entry_icon.get_style_context().remove_class(const.ERROR)
        self.check_icon.get_style_context().remove_class(const.ERROR)
        self.check_color.get_style_context().remove_class(const.ERROR)
        self.check_scale.get_style_context().remove_class(const.ERROR)
        self.check_opacity.get_style_context().remove_class(const.ERROR)
