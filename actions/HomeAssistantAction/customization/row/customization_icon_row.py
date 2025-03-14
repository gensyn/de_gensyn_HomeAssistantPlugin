"""
The module for the Home Assistant customization row.
"""
from typing import List, Dict

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_row \
    import CustomizationRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import icon_helper


class CustomizationIconRow(CustomizationRow):
    """
    Base for customization icon rows
    """

    def __init__(self, lm, customization: Dict, customizations: List, index: int, attributes: List,
                 state: Dict, settings: Dict):
        super().__init__(lm, customizations, index, attributes, state, settings)

        current_value = icon_helper.get_value(state, customization)

        title = self._init_title(customization, current_value)

        if customization.get(const.CUSTOM_ICON_ICON) is not None:
            title += (f"\n{self.lm.get(const.LABEL_ICON_ICON)} "
                      f"{customization[const.CUSTOM_ICON_ICON]}")

        if customization.get(const.CUSTOM_ICON_COLOR) is not None:
            color = customization[const.CUSTOM_ICON_COLOR]
            color = (f'#{int(round(color[0] * 255, 0)):02X}'
                     f'{int(round(color[1] * 255, 0)):02X}'
                     f'{int(round(color[2] * 255, 0)):02X}')
            title += (f"\n{self.lm.get(const.LABEL_ICON_COLOR)} "
                      f"{color}")

        if customization.get(const.CUSTOM_ICON_SCALE) is not None:
            title += (f"\n{self.lm.get(const.LABEL_ICON_SCALE)} "
                      f"{int(customization[const.CUSTOM_ICON_SCALE])}")

        if customization.get(const.CUSTOM_ICON_OPACITY) is not None:
            title += (f"\n{self.lm.get(const.LABEL_ICON_OPACITY)} "
                      f"{int(customization[const.CUSTOM_ICON_OPACITY])}")

        self.set_title(title)
