"""
The module for the Home Assistant customization row.
"""
from typing import List, Dict

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.icon_customization import IconCustomization
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_row \
    import CustomizationRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import icon_helper, helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.settings.settings import Settings


class CustomizationIconRow(CustomizationRow):
    """
    Base for customization icon rows
    """

    def __init__(self, lm, customization: IconCustomization, customization_count: int, index: int, attributes: List,
                 state: Dict, settings: Settings):
        super().__init__(lm, customization_count, index, attributes, state, settings)

        current_value = icon_helper.get_value(state, customization)

        title = self._init_title(customization, current_value)

        if customization.get_icon() is not None:
            title += (f"\n{self.lm.get(const.LABEL_ICON_ICON)} "
                      f"{customization.get_icon()}")

        if customization.get_color() is not None:
            color = helper.convert_color_list_to_hex(customization.get_color())
            title += (f"\n{self.lm.get(const.LABEL_ICON_COLOR)} "
                      f"{color}")

        if customization.get_scale() is not None:
            title += (f"\n{self.lm.get(const.LABEL_ICON_SCALE)} "
                      f"{int(customization.get_scale())}")

        if customization.get_opacity() is not None:
            title += (f"\n{self.lm.get(const.LABEL_ICON_OPACITY)} "
                      f"{int(customization.get_opacity())}")

        self.set_title(title)
