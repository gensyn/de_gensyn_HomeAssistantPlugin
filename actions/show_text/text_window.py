"""
The module for the Home Assistant customization text window.
"""

from functools import partial
from typing import Callable, List

from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from de_gensyn_HomeAssistantPlugin.actions import const as base_const
from de_gensyn_HomeAssistantPlugin.actions.show_text import text_const
from de_gensyn_HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_window import CustomizationWindow


class TextWindow(CustomizationWindow):
    """
    Window to customize text.
    """

    def __init__(self, lm, attributes: List, callback: Callable,
                 current: TextCustomization = None, index: int = None):
        super().__init__(lm, attributes, callback, current, index)

        self.set_title(lm.get(text_const.CUSTOMIZATION_WINDOW_TITLE))

        # add text_length to attributes
        self.combo_attribute.get_model().insert(0, [text_const.CUSTOM_TEXT_LENGTH])

        #
        # check buttons
        #

        self.check_position = self._create_check_button()
        self.check_text_attribute = self._create_check_button()
        self.check_round = self._create_check_button()
        self.check_precision = self._create_check_button()
        self.check_text_size = self._create_check_button()
        self.check_text_color = self._create_check_button()
        self.check_outline_size = self._create_check_button()
        self.check_outline_color = self._create_check_button()
        self.check_show_unit = self._create_check_button()
        self.check_line_break = self._create_check_button()

        #
        # labels
        #

        label_position = self._create_label(self.lm.get(text_const.LABEL_POSITION))
        label_text_attribute = self._create_label(self.lm.get(text_const.LABEL_ATTRIBUTE))
        label_round = self._create_label(self.lm.get(text_const.LABEL_ROUND))
        label_precision = self._create_label(self.lm.get(text_const.LABEL_ROUND_PRECISION))
        label_text_size = self._create_label(self.lm.get(text_const.LABEL_TEXT_SIZE))
        label_text_color = self._create_label(self.lm.get(text_const.LABEL_TEXT_COLOR))
        label_outline_size = self._create_label(self.lm.get(text_const.LABEL_OUTLINE_SIZE))
        label_outline_color = self._create_label(self.lm.get(text_const.LABEL_OUTLINE_COLOR))
        label_show_unit = self._create_label(self.lm.get(text_const.LABEL_SHOW_UNIT_SHORT))
        label_line_break = self._create_label(self.lm.get(text_const.LABEL_UNIT_LINE_BREAK_SHORT))

        #
        # widgets
        #

        positions = [text_const.POSITION_TOP, text_const.POSITION_CENTER,
                     text_const.POSITION_BOTTOM]
        self.combo_position = self._create_combo(positions, self.check_position)

        attributes = [text_const.CUSTOM_CUSTOM_TEXT]
        attributes.extend(self.attributes)
        self.combo_text_attribute = self._create_combo(attributes, self.check_text_attribute)
        self.connect_rows.append(
            partial(self.combo_text_attribute.connect, base_const.CONNECT_CHANGED,
                    self._on_change_text_attribute))
        self.entry_custom_text = self._create_entry(None)

        self.switch_round = self._create_switch(self.check_round)

        self.scale_precision = self._create_scale(text_const.ROUND_MIN_PRECISION,
                                                  text_const.ROUND_MAX_PRECISION, 1,
                                                  self.check_precision)

        self.entry_precision = self._create_scale_entry(self.check_precision)
        self.entry_precision.set_hexpand(True)

        self.connect_rows.append(
            partial(self.scale_precision.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.entry_precision, text_const.ROUND_MIN_PRECISION,
                    text_const.ROUND_MAX_PRECISION))
        self.connect_rows.append(
            partial(self.entry_precision.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.scale_precision,
                    text_const.ROUND_MIN_PRECISION,
                    text_const.ROUND_MAX_PRECISION))

        self.scale_text_size = self._create_scale(text_const.TEXT_MIN_SIZE,
                                                  text_const.TEXT_MAX_SIZE, 1, self.check_text_size)

        self.entry_text_size = self._create_scale_entry(self.check_text_size)

        self.connect_rows.append(
            partial(self.scale_text_size.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.entry_text_size, text_const.TEXT_MIN_SIZE,
                    text_const.TEXT_MAX_SIZE))
        self.connect_rows.append(
            partial(self.entry_text_size.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.scale_text_size, text_const.TEXT_MIN_SIZE,
                    text_const.TEXT_MAX_SIZE))

        self.button_text_color = self._create_color_button(self.check_text_color)

        self.scale_outline_size = self._create_scale(text_const.OUTLINE_MIN_SIZE,
                                                     text_const.OUTLINE_MAX_SIZE, 1,
                                                     self.check_outline_size)

        self.entry_outline_size = self._create_scale_entry(self.check_outline_size)

        self.connect_rows.append(
            partial(self.scale_outline_size.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.entry_outline_size, text_const.OUTLINE_MIN_SIZE,
                    text_const.OUTLINE_MAX_SIZE))
        self.connect_rows.append(
            partial(self.entry_outline_size.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.scale_outline_size,
                    text_const.OUTLINE_MIN_SIZE,
                    text_const.OUTLINE_MAX_SIZE))

        self.button_outline_color = self._create_color_button(self.check_outline_color)

        self.switch_show_unit = self._create_switch(self.check_show_unit)

        self.switch_line_break = self._create_switch(self.check_line_break)

        #
        # add to ui
        #

        self.grid_fields.attach(self.check_position, 2, 2, 1, 1)
        self.grid_fields.attach(label_position, 3, 2, 1, 1)
        self.grid_fields.attach(self.combo_position, 4, 2, 1, 1)

        self.grid_fields.attach(self.check_text_attribute, 2, 3, 1, 1)
        self.grid_fields.attach(label_text_attribute, 3, 3, 1, 1)
        self.grid_fields.attach(self.combo_text_attribute, 4, 3, 1, 1)
        self.grid_fields.attach(self.entry_custom_text, 5, 3, 1, 1)

        self.grid_fields.attach(self.check_round, 2, 4, 1, 1)
        self.grid_fields.attach(label_round, 3, 4, 1, 1)
        self.grid_fields.attach(self.switch_round, 4, 4, 1, 1)

        self.grid_fields.attach(self.check_precision, 2, 5, 1, 1)
        self.grid_fields.attach(label_precision, 3, 5, 1, 1)
        self.grid_fields.attach(self.scale_precision, 4, 5, 1, 1)
        self.grid_fields.attach(self.entry_precision, 5, 5, 1, 1)

        self.grid_fields.attach(self.check_text_size, 2, 6, 1, 1)
        self.grid_fields.attach(label_text_size, 3, 6, 1, 1)
        self.grid_fields.attach(self.scale_text_size, 4, 6, 1, 1)
        self.grid_fields.attach(self.entry_text_size, 5, 6, 1, 1)

        self.grid_fields.attach(self.check_text_color, 2, 7, 1, 1)
        self.grid_fields.attach(label_text_color, 3, 7, 1, 1)
        self.grid_fields.attach(self.button_text_color, 4, 7, 1, 1)

        self.grid_fields.attach(self.check_outline_size, 2, 8, 1, 1)
        self.grid_fields.attach(label_outline_size, 3, 8, 1, 1)
        self.grid_fields.attach(self.scale_outline_size, 4, 8, 1, 1)
        self.grid_fields.attach(self.entry_outline_size, 5, 8, 1, 1)

        self.grid_fields.attach(self.check_outline_color, 2, 9, 1, 1)
        self.grid_fields.attach(label_outline_color, 3, 9, 1, 1)
        self.grid_fields.attach(self.button_outline_color, 4, 9, 1, 1)

        self.grid_fields.attach(self.check_show_unit, 2, 10, 1, 1)
        self.grid_fields.attach(label_show_unit, 3, 10, 1, 1)
        self.grid_fields.attach(self.switch_show_unit, 4, 10, 1, 1)

        self.grid_fields.attach(self.check_line_break, 2, 11, 1, 1)
        self.grid_fields.attach(label_line_break, 3, 11, 1, 1)
        self.grid_fields.attach(self.switch_line_break, 4, 11, 1, 1)

        self._after_init()

    def _on_change_text_attribute(self, _) -> None:
        if self.combo_text_attribute.get_model()[self.combo_text_attribute.get_active()][
            0] == text_const.CUSTOM_CUSTOM_TEXT:
            self.entry_custom_text.set_visible(True)
            return
        self.entry_custom_text.set_visible(False)

    def _set_default_values(self) -> None:
        super()._set_default_values()

        for index, entry in enumerate(self.combo_position.get_model()):
            if entry[0] == text_const.DEFAULT_POSITION:
                self.combo_position.set_active(index)
                break

        for index, entry in enumerate(self.combo_text_attribute.get_model()):
            if entry[0] == text_const.DEFAULT_ATTRIBUTE:
                self.combo_text_attribute.set_active(index)
                break

        self.entry_custom_text.set_text(text_const.DEFAULT_CUSTOM_TEXT)
        self.entry_custom_text.set_visible(False)
        self.switch_round.set_active(text_const.DEFAULT_ROUND)
        self.scale_precision.set_value(text_const.DEFAULT_ROUND_PRECISION)
        self.entry_precision.set_text(str(text_const.DEFAULT_ROUND_PRECISION))
        self.scale_text_size.set_value(text_const.DEFAULT_TEXT_SIZE)
        self.entry_text_size.set_text(str(text_const.DEFAULT_TEXT_SIZE))

        text_rgba = customization_helper.convert_color_list_to_rgba(text_const.DEFAULT_TEXT_COLOR)
        self.button_text_color.set_rgba(text_rgba)

        self.scale_outline_size.set_value(text_const.DEFAULT_OUTLINE_SIZE)
        self.entry_outline_size.set_text(str(text_const.DEFAULT_OUTLINE_SIZE))

        outline_rgba = customization_helper.convert_color_list_to_rgba(text_const.DEFAULT_OUTLINE_COLOR)
        self.button_outline_color.set_rgba(outline_rgba)

        self.switch_show_unit.set_active(text_const.DEFAULT_SHOW_UNIT)

        self.switch_line_break.set_active(text_const.DEFAULT_UNIT_LINE_BREAK)

    def _set_current_values(self) -> None:
        if not self.current:
            return

        super()._set_current_values()

        for index, entry in enumerate(self.combo_position.get_model()):
            if entry[0] == self.current.get_position():
                self.combo_position.set_active(index)
                break
        self.check_position.set_active(self.current.get_position() is not None)

        for index, entry in enumerate(self.combo_text_attribute.get_model()):
            if entry[0] == self.current.get_text_attribute():
                self.combo_text_attribute.set_active(index)
                break
        self.check_text_attribute.set_active(self.current.get_text_attribute() is not None)

        self.entry_custom_text.set_text(
            self.current.get_custom_text() or text_const.DEFAULT_CUSTOM_TEXT)
        self.entry_custom_text.set_visible(
            self.current.get_custom_text() is not None)

        self.switch_round.set_active(self.current.get_round() or text_const.DEFAULT_ROUND)
        self.check_round.set_active(self.current.get_round() is not None)

        self.scale_precision.set_value(
            self.current.get_round_precision() or text_const.DEFAULT_ROUND_PRECISION)
        self.entry_precision.set_text(
            str(self.current.get_round_precision() or text_const.DEFAULT_ROUND_PRECISION))
        self.check_precision.set_active(self.current.get_round_precision() is not None)

        self.scale_text_size.set_value(
            self.current.get_text_size() or text_const.DEFAULT_TEXT_SIZE)
        self.entry_text_size.set_text(
            str(self.current.get_text_size() or text_const.DEFAULT_TEXT_SIZE))
        self.check_text_size.set_active(self.current.get_text_size() is not None)

        if self.current.get_text_color():
            text_rgba = customization_helper.convert_color_list_to_rgba(self.current.get_text_color())
            self.button_text_color.set_rgba(text_rgba)
        self.check_text_color.set_active(self.current.get_text_color() is not None)

        self.scale_outline_size.set_value(
            self.current.get_outline_size() or text_const.DEFAULT_OUTLINE_SIZE)
        self.entry_outline_size.set_text(
            str(self.current.get_outline_size() or text_const.DEFAULT_OUTLINE_SIZE))
        self.check_outline_size.set_active(self.current.get_outline_size() is not None)

        if self.current.get_outline_color():
            outline_rgba = customization_helper.convert_color_list_to_rgba(
                self.current.get_outline_color())
            self.button_outline_color.set_rgba(outline_rgba)
        self.check_outline_color.set_active(self.current.get_outline_color() is not None)

        self.switch_show_unit.set_active(
            self.current.get_show_unit() or text_const.DEFAULT_SHOW_UNIT)
        self.check_show_unit.set_active(self.current.get_show_unit() is not None)

        self.switch_line_break.set_active(
            self.current.get_line_break() or text_const.DEFAULT_UNIT_LINE_BREAK)
        self.check_line_break.set_active(self.current.get_line_break() is not None)

    def _on_add_button(self, _) -> None:
        if not super()._on_add_button(_):
            return

        if self.check_position.get_active() and self.combo_position.get_active() < 0:
            self.combo_position.get_style_context().add_class(text_const.ERROR)
            return

        if self.check_text_attribute.get_active() and self.combo_text_attribute.get_active() < 0:
            self.combo_text_attribute.get_style_context().add_class(text_const.ERROR)
            return

        if (not self.check_position.get_active() and not self.check_text_attribute.get_active()
                and not self.check_round.get_active() and not self.check_precision.get_active()
                and not self.check_text_size.get_active() and not self.check_text_color.get_active()
                and not self.check_outline_size.get_active() and not
                self.check_outline_color.get_active()
                and not self.check_show_unit.get_active() and not
                self.check_line_break.get_active()):
            self.check_position.get_style_context().add_class(text_const.ERROR)
            self.check_text_attribute.get_style_context().add_class(text_const.ERROR)
            self.check_round.get_style_context().add_class(text_const.ERROR)
            self.check_precision.get_style_context().add_class(text_const.ERROR)
            self.check_text_size.get_style_context().add_class(text_const.ERROR)
            self.check_text_color.get_style_context().add_class(text_const.ERROR)
            self.check_outline_size.get_style_context().add_class(text_const.ERROR)
            self.check_outline_color.get_style_context().add_class(text_const.ERROR)
            self.check_show_unit.get_style_context().add_class(text_const.ERROR)
            self.check_line_break.get_style_context().add_class(text_const.ERROR)
            return

        attribute = \
            self.combo_attribute.get_model()[self.combo_attribute.get_active()][0]
        value = self.entry_value.get_text()

        if attribute == text_const.CUSTOM_TEXT_LENGTH and not self._is_number(value):
            # operator needs a number
            self.combo_operator.get_style_context().add_class(text_const.ERROR)
            self.entry_value.get_style_context().add_class(text_const.ERROR)
            return

        text_attribute = \
            self.combo_text_attribute.get_model()[self.combo_text_attribute.get_active()][
                0] if self.check_text_attribute.get_active() else None
        position = self.combo_position.get_model()[self.combo_position.get_active()][
            0] if self.check_position.get_active() else None
        custom_text = self.entry_custom_text.get_text() \
            if (self.check_text_attribute.get_active() and
                self.combo_text_attribute.get_model()[self.combo_text_attribute.get_active()][0]
                == text_const.CUSTOM_CUSTOM_TEXT) else None
        text_round = self.switch_round.get_active() if self.check_round.get_active() else None
        precision = int(
            self.scale_precision.get_value()) if self.check_precision.get_active() else None
        text_size = int(
            self.scale_text_size.get_value()) if self.check_text_size.get_active() else None
        text_color = self.button_text_color.get_rgba() if self.check_text_color.get_active() else \
            None
        text_color_list = customization_helper.convert_rgba_to_color_list(text_color) if text_color else None
        outline_size = int(
            self.scale_outline_size.get_value()) if self.check_outline_size.get_active() else None
        outline_color = self.button_outline_color.get_rgba() if (
            self.check_outline_color.get_active()) else None
        outline_color_list = customization_helper.convert_rgba_to_color_list(outline_color) if outline_color else None
        show_unit = self.switch_show_unit.get_active() if self.check_show_unit.get_active() else \
            None
        line_break = self.switch_line_break.get_active() if self.check_line_break.get_active() \
            else None

        self.callback(TextCustomization(
            attribute=attribute,
            operator=self.combo_operator.get_model()[self.combo_operator.get_active()][0],
            value=value,
            position=position, text_attribute=text_attribute, custom_text=custom_text,
            do_round=text_round, round_precision=precision,
            text_size=text_size, text_color=text_color_list, outline_size=outline_size,
            outline_color=outline_color_list, show_unit=show_unit, line_break=line_break),
            index=self.index)

        self.destroy()

    def _on_widget_changed(self, _):
        super()._on_widget_changed(_)

        self.check_position.get_style_context().remove_class(text_const.ERROR)
        self.combo_position.get_style_context().remove_class(text_const.ERROR)
        self.check_text_attribute.get_style_context().remove_class(text_const.ERROR)
        self.combo_text_attribute.get_style_context().remove_class(text_const.ERROR)
        self.entry_custom_text.get_style_context().remove_class(text_const.ERROR)
        self.check_round.get_style_context().remove_class(text_const.ERROR)
        self.check_precision.get_style_context().remove_class(text_const.ERROR)
        self.check_text_size.get_style_context().remove_class(text_const.ERROR)
        self.check_show_unit.get_style_context().remove_class(text_const.ERROR)
        self.check_line_break.get_style_context().remove_class(text_const.ERROR)
