"""Module to manage HomeAssistantPlugin action settings."""

from typing import List

from de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_settings import BaseSettings
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_const
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization import Customization


class CustomizationSettings(BaseSettings):
    """
    Class to manage all settings for an HomeAssistantPlugin action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action, customization_name, customization_implementation):
        super().__init__(action)

        self.customization_name = customization_name
        self.customization_implementation = customization_implementation

    def get_customizations(self):
        return [self.customization_implementation.from_dict(c) for c in self._settings[self.customization_name][customization_const.SETTING_CUSTOMIZATIONS]]

    def move_customization(self, index: int, places_count: int):
        """
        Move the customization at the index by x places.
        :param index: the index to move
        :param places_count: to number of places to move; may be negative
        :return:
        """
        customization_list = self._settings[self.customization_name][customization_const.SETTING_CUSTOMIZATIONS]
        self._move_customization(customization_list, index, places_count)

    def _move_customization(self, customization_list: List, index: int, places_count: int):
        customization = customization_list.pop(index)
        customization_list.insert(index + places_count, customization)
        self._action.set_settings(self._settings)

    def remove_customization(self, index: int) -> None:
        """
        Remove the customization at the index.
        :param index: the index to remove
        :return:
        """
        self._settings[self.customization_name][customization_const.SETTING_CUSTOMIZATIONS].pop(index)
        self._action.set_settings(self._settings)

    def replace_customization(self, index: int, customization: Customization) -> None:
        """
        Replace the customization at the index.
        :param index: the index to replace
        :param customization: the new customization
        :return:
        """
        self._settings[self.customization_name][customization_const.SETTING_CUSTOMIZATIONS][index] = customization.export()
        self._action.set_settings(self._settings)

    def add_customization(self, customization: Customization) -> None:
        """
        Add a new customization.
        :param customization: the new customization
        """
        self._settings[self.customization_name][customization_const.SETTING_CUSTOMIZATIONS].append(customization.export())
        self._action.set_settings(self._settings)