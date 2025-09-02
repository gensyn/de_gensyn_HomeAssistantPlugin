"""
The module for the Home Assistant customization icon window.
"""

from functools import partial
from typing import Callable, List

from de_gensyn_HomeAssistantPlugin.actions import const as base_const
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_window import CustomizationWindow
from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_const, icon_helper
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization


class IconWindow(CustomizationWindow):
    """
    Window to customize icons.
    """

    def __init__(self, lm, attributes: List, callback: Callable,
                 current: IconCustomization = None, index: int = None):
        super().__init__(lm, attributes, callback, current, index)

        self.icons: List[str] = list(icon_helper.MDI_ICONS)

        self.set_title(lm.get(icon_const.CUSTOMIZATION_WINDOW_TITLE))

        self.check_icon = self._create_check_button()
        self.check_color = self._create_check_button()
        self.check_scale = self._create_check_button()
        self.check_opacity = self._create_check_button()

        label_icon = self._create_label(self.lm.get(icon_const.LABEL_ICON_ICON))
        label_color = self._create_label(self.lm.get(icon_const.LABEL_ICON_COLOR))
        label_scale = self._create_label(self.lm.get(icon_const.LABEL_ICON_SCALE))
        label_opacity = self._create_label(self.lm.get(icon_const.LABEL_ICON_OPACITY))

        self.icon = self._create_entry(self.check_icon)
        self.icon.set_margin_end(self.default_margin)
        self.connect_rows.append(
            partial(self.icon.connect, base_const.CONNECT_ACTIVATE, self._on_widget_changed))

        self.color = self._create_color_button(self.check_color)

        self.scale = self._create_scale(icon_const.ICON_MIN_SCALE, icon_const.ICON_MAX_SCALE, 1,
                                        self.check_scale)

        self.scale_entry = self._create_scale_entry(self.check_scale)
        self.scale_entry.set_hexpand(True)

        self.connect_rows.append(
            partial(self.scale.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.scale_entry, icon_const.ICON_MIN_SCALE,
                    icon_const.ICON_MAX_SCALE))
        self.connect_rows.append(
            partial(self.scale_entry.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.scale, icon_const.ICON_MIN_SCALE,
                    icon_const.ICON_MAX_SCALE))

        self.opacity = self._create_scale(icon_const.ICON_MIN_OPACITY, icon_const.ICON_MAX_OPACITY, 1,
                                          self.check_opacity)

        self.opacity_entry = self._create_scale_entry(self.check_opacity)
        self.opacity_entry.set_hexpand(True)

        self.connect_rows.append(
            partial(self.opacity.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.opacity_entry, icon_const.ICON_MIN_OPACITY,
                    icon_const.ICON_MAX_OPACITY))
        self.connect_rows.append(
            partial(self.opacity_entry.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.opacity, icon_const.ICON_MIN_OPACITY,
                    icon_const.ICON_MAX_OPACITY))

        self.grid_fields.attach(self.check_icon, 2, 2, 1, 1)
        self.grid_fields.attach(label_icon, 3, 2, 1, 1)
        self.grid_fields.attach(self.icon, 4, 2, 1, 1)

        self.grid_fields.attach(self.check_color, 2, 3, 1, 1)
        self.grid_fields.attach(label_color, 3, 3, 1, 1)
        self.grid_fields.attach(self.color, 4, 3, 1, 1)

        self.grid_fields.attach(self.check_scale, 2, 4, 1, 1)
        self.grid_fields.attach(label_scale, 3, 4, 1, 1)
        self.grid_fields.attach(self.scale, 4, 4, 1, 1)
        self.grid_fields.attach(self.scale_entry, 5, 4, 1, 1)

        self.grid_fields.attach(self.check_opacity, 2, 5, 1, 1)
        self.grid_fields.attach(label_opacity, 3, 5, 1, 1)
        self.grid_fields.attach(self.opacity, 4, 5, 1, 1)
        self.grid_fields.attach(self.opacity_entry, 5, 5, 1, 1)

        self._after_init()

    def _set_default_values(self) -> None:
        super()._set_default_values()

        rgba = customization_helper.convert_color_list_to_rgba(icon_const.DEFAULT_ICON_COLOR)
        self.color.set_rgba(rgba)

        self.scale.set_value(icon_const.DEFAULT_ICON_SCALE)
        self.scale_entry.set_text(str(icon_const.DEFAULT_ICON_SCALE))

        self.opacity.set_value(icon_const.DEFAULT_ICON_OPACITY)
        self.opacity_entry.set_text(str(icon_const.DEFAULT_ICON_OPACITY))

    def _set_current_values(self) -> None:
        if not self.current:
            return

        super()._set_current_values()

        self.icon.set_text(self.current.get_icon() or icon_const.EMPTY_STRING)
        self.check_icon.set_active(self.current.get_icon() is not None)

        if self.current.get_color():
            rgba = customization_helper.convert_color_list_to_rgba(self.current.get_color())
            self.color.set_rgba(rgba)
        self.check_color.set_active(self.current.get_color() is not None)

        self.scale.set_value(
            self.current.get_scale() or icon_const.DEFAULT_ICON_SCALE)
        self.check_scale.set_active(self.current.get_scale() is not None)
        self.scale_entry.set_text(
            str(int(self.current.get_scale() or icon_const.DEFAULT_ICON_SCALE)))

        self.opacity.set_value(
            self.current.get_opacity() or icon_const.DEFAULT_ICON_OPACITY)
        self.check_opacity.set_active(self.current.get_opacity() is not None)
        self.opacity_entry.set_text(
            str(int(self.current.get_opacity() or icon_const.DEFAULT_ICON_OPACITY)))

    def _on_add_button(self, _):
        if not super()._on_add_button(_):
            return

        if self.check_icon.get_active():
            icon = self.icon.get_text()

            if icon.startswith("mdi:"):
                icon = icon[4:]

            if self.operator.get_selected_item().value in (
                    "<", "<=", ">", ">="):
                # expecting a number in value
                try:
                    float(self.entry_value.get_text())
                except ValueError:
                    self.operator.add_css_class(icon_const.ERROR)
                    self.entry_value.add_css_class(icon_const.ERROR)
                    return

            if icon not in self.icons:
                self.icon.add_css_class(icon_const.ERROR)
                return

        if (not self.check_icon.get_active() and not self.check_color.get_active() and not
        self.check_scale.get_active() and not self.check_opacity.get_active()):
            self.check_icon.add_css_class(icon_const.ERROR)
            self.check_color.add_css_class(icon_const.ERROR)
            self.check_scale.add_css_class(icon_const.ERROR)
            self.check_opacity.add_css_class(icon_const.ERROR)
            return

        icon = self.icon.get_text() if self.check_icon.get_active() else None
        color = self.color.get_rgba() if self.check_color.get_active() else None
        color_list = customization_helper.convert_rgba_to_color_list(color) if color else None
        scale = int(self.scale.get_value()) if self.check_scale.get_active() else None
        opacity = int(
            self.opacity.get_value()) if self.check_opacity.get_active() else None

        self.callback(customization=IconCustomization(
            attribute=self.condition_attribute.get_selected_item().get_string(),
            operator=self.operator.get_selected_item().value,
            value=self.entry_value.get_text(), icon=icon, color=color_list, scale=scale,
            opacity=opacity), index=self.index)

        self.destroy()

    def _on_widget_changed(self, *args, **kwargs) -> None:
        super()._on_widget_changed()

        self.icon.remove_css_class(icon_const.ERROR)
        self.check_icon.remove_css_class(icon_const.ERROR)
        self.check_color.remove_css_class(icon_const.ERROR)
        self.check_scale.remove_css_class(icon_const.ERROR)
        self.check_opacity.remove_css_class(icon_const.ERROR)
