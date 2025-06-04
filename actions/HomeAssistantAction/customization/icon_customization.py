"""
Modul to manage icon customizations.
"""

from typing import Tuple, Dict, Any

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.customization import Customization


class IconCustomization(Customization):
    """
    Class to represent an icon customization.
    """
    def __init__(self, attribute: str, operator: str, value: str, icon: str, color: Tuple[int, int, int, int],
                 scale: int, opacity: int):
        super().__init__(attribute, operator, value)
        self.icon: str = icon
        self.color: Tuple[int, int, int, int] = color
        self.scale: int = scale
        self.opacity: int = opacity

    def get_icon(self) -> str:
        """
        Get the icon.
        :return:the icon
        """
        return self.icon

    def get_color(self) -> Tuple[int, int, int, int]:
        """
        Get the icon color.
        :return:the icon color
        """
        return self.color

    def get_scale(self) -> int:
        """
        Get the icon scale.
        :return: the icon scale
        """
        return self.scale

    def get_opacity(self) -> int:
        """
        Get the icon opacity.
        :return: the icon opacity
        """
        return self.opacity

    def export(self) -> Dict[str, Any]:
        """
        Get this customization as a dict.
        :return: this customization as a dict
        """
        return {
            const.CUSTOM_CONDITION: {
                const.CUSTOM_ATTRIBUTE: self.attribute,
                const.CUSTOM_OPERATOR: self.operator,
                const.CUSTOM_VALUE: self.value
            },
            const.CUSTOM_ICON_ICON: self.icon,
            const.CUSTOM_ICON_COLOR: self.color,
            const.CUSTOM_ICON_SCALE: self.scale,
            const.CUSTOM_ICON_OPACITY: self.opacity
        }
