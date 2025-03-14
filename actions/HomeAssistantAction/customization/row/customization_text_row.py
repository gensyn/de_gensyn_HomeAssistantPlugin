"""
The module for the Home Assistant customization row.
"""
from typing import List, Dict

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_row \
    import CustomizationRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import text_helper


class CustomizationTextRow(CustomizationRow):
    """
    Base for customization icon rows
    """

    def __init__(self, lm, customization: Dict, customizations: List, index: int, attributes: List,
                 state: Dict, settings: Dict):
        super().__init__(lm, customizations, index, attributes, state, settings)

        current_value = text_helper.get_value(self.state, self.settings, customization)

        title = self._init_title(customization, current_value)

        if customization.get(const.CUSTOM_TEXT_POSITION) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_POSITION)} "
                      f"{customization[const.CUSTOM_TEXT_POSITION]}")

        if customization.get(const.CUSTOM_TEXT_ATTRIBUTE) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_ATTRIBUTE)} "
                      f"{customization[const.CUSTOM_TEXT_ATTRIBUTE]}")
            if customization.get(const.CUSTOM_TEXT_CUSTOM_TEXT) is not None:
                title += f" = \"{customization[const.CUSTOM_TEXT_CUSTOM_TEXT]}\""

        if customization.get(const.CUSTOM_TEXT_ROUND) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_ROUND)} "
                      f"{customization[const.CUSTOM_TEXT_ROUND]}")

        if customization.get(const.CUSTOM_TEXT_ROUND_PRECISION) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_ROUND_PRECISION)} "
                      f"{customization[const.CUSTOM_TEXT_ROUND_PRECISION]}")

        if customization.get(const.CUSTOM_TEXT_TEXT_SIZE) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_TEXT_SIZE)} "
                      f"{customization[const.CUSTOM_TEXT_TEXT_SIZE]}")

        if customization.get(const.CUSTOM_TEXT_TEXT_COLOR) is not None:
            color = customization[const.CUSTOM_TEXT_TEXT_COLOR]
            color = (f'#{int(round(color[0] * 255, 0)):02X}'
                     f'{int(round(color[1] * 255, 0)):02X}'
                     f'{int(round(color[2] * 255, 0)):02X}')
            title += (f"\n{self.lm.get(const.LABEL_TEXT_TEXT_COLOR)} "
                      f"{color}")

        if customization.get(const.CUSTOM_TEXT_OUTLINE_SIZE) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_OUTLINE_SIZE)} "
                      f"{customization[const.CUSTOM_TEXT_OUTLINE_SIZE]}")

        if customization.get(const.CUSTOM_TEXT_OUTLINE_COLOR) is not None:
            color = customization[const.CUSTOM_TEXT_OUTLINE_COLOR]
            color = (f'#{int(round(color[0] * 255, 0)):02X}'
                     f'{int(round(color[1] * 255, 0)):02X}'
                     f'{int(round(color[2] * 255, 0)):02X}')
            title += (f"\n{self.lm.get(const.LABEL_TEXT_OUTLINE_COLOR)} "
                      f"{color}")

        if customization.get(const.CUSTOM_TEXT_SHOW_UNIT) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_SHOW_UNIT_SHORT)} "
                      f"{customization[const.CUSTOM_TEXT_SHOW_UNIT]}")

        if customization.get(const.CUSTOM_TEXT_LINE_BREAK) is not None:
            title += (f"\n{self.lm.get(const.LABEL_TEXT_UNIT_LINE_BREAK_SHORT)} "
                      f"{customization[const.CUSTOM_TEXT_LINE_BREAK]}")

        self.set_title(title)
