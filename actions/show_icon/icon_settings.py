"""Module to manage action settings."""

from typing import Tuple

from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_const
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings
from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_const
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization

DEFAULT_SETTINGS = {
    icon_const.SETTING_ICON: icon_const.EMPTY_STRING,
    icon_const.SETTING_COLOR: icon_const.DEFAULT_ICON_COLOR,
    icon_const.SETTING_SCALE: icon_const.DEFAULT_ICON_SCALE,
    icon_const.SETTING_OPACITY: icon_const.DEFAULT_ICON_OPACITY,
    customization_const.SETTING_CUSTOMIZATIONS: []
}


class ShowIconSettings(CustomizationSettings):
    """
    Class to manage all settings for a "Perform Action" action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action):
        super().__init__(action, icon_const.SETTING_ICON, IconCustomization)

        self._icon = None
        self._color = None
        self._scale = None
        self._opacity = None

        if not self._settings.get(icon_const.SETTING_ICON):
            self._settings[icon_const.SETTING_ICON] = DEFAULT_SETTINGS.copy()
            self._action.set_settings(self._settings)

        self.load()

    def get_icon(self) -> str:
        """
        Get the icon.
        :return: the icon
        """
        return self._icon

    def get_color(self) -> Tuple[int, int, int, int]:
        """
        Get the color.
        :return: the color
        """
        return self._color

    def get_scale(self) -> int:
        """
        Get the scale.
        :return: the scale
        """
        return int(self._scale)

    def get_opacity(self) -> int:
        """
        Get the opacity.
        :return: the opacity
        """
        return int(self._opacity)

    def load(self) -> None:
        """
        Loads the settings from the action.
        :return: None
        """
        super().load()
        self._icon = self._settings[icon_const.SETTING_ICON][icon_const.SETTING_ICON]
        self._color = self._settings[icon_const.SETTING_ICON][icon_const.SETTING_COLOR]
        self._scale = self._settings[icon_const.SETTING_ICON][icon_const.SETTING_SCALE]
        self._opacity = self._settings[icon_const.SETTING_ICON][icon_const.SETTING_OPACITY]
