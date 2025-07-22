"""
The module for the Home Assistant customization row.
"""
from typing import List, Dict

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_row \
    import CustomizationRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.text_customization import TextCustomization
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import text_helper, helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.settings.settings import Settings


class CustomizationTextRow(CustomizationRow):
    """
    Base for customization icon rows
    """

    def __init__(self, lm, customization: TextCustomization, customization_count: int, index: int, attributes: List,
                 state: Dict, settings: Settings):
        super().__init__(lm, customization_count, index, attributes, state, settings)

        current_value = text_helper.get_value(self.state, self.settings, customization)

        title = self._init_title(customization, current_value)

        if customization.get_position() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_POSITION)} "
                      f"{customization.get_position()}")

        if customization.get_attribute() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_ATTRIBUTE)} "
                      f"{customization.get_attribute()}")
            if customization.get_custom_text() is not None:
                title += f" = \"{customization.get_custom_text()}\""

        if customization.get_round() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_ROUND)} "
                      f"{customization.get_round()}")

        if customization.get_round_precision() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_ROUND_PRECISION)} "
                      f"{customization.get_round_precision()}")

        if customization.get_text_size() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_TEXT_SIZE)} "
                      f"{customization.get_text_size()}")

        if customization.get_text_color() is not None:
            color = helper.convert_color_list_to_hex(customization.get_text_color())
            title += (f"\n{self.lm.get(const.LABEL_TEXT_TEXT_COLOR)} "
                      f"{color}")

        if customization.get_outline_size() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_OUTLINE_SIZE)} "
                      f"{customization.get_outline_size()}")

        if customization.get_outline_color() is not None:
            color = helper.convert_color_list_to_hex(customization.get_outline_color())
            title += (f"\n{self.lm.get(const.LABEL_TEXT_OUTLINE_COLOR)} "
                      f"{color}")

        if customization.get_show_unit() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_SHOW_UNIT_SHORT)} "
                      f"{customization.get_show_unit()}")

        if customization.get_line_break() is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_UNIT_LINE_BREAK_SHORT)} "
                      f"{customization.get_line_break()}")

        self.set_title(title)
