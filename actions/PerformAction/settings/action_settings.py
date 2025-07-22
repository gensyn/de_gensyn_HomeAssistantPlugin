"""Module to manage action settings."""

from typing import Dict

from de_gensyn_HomeAssistantPlugin.actions.PerformAction import const
from de_gensyn_HomeAssistantPlugin.actions.settings.settings import Settings

DEFAULT_SETTINGS = {
    const.SETTING_ACTION: const.EMPTY_STRING,
    const.ACTION_PARAMETERS: {}
}


class ActionSettings(Settings):
    """
    Class to manage all settings for an HomeAssistantPlugin action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action):
        super().__init__(action)

        self._ha_action = None
        self._parameters = None

        if not self._settings.get(const.SETTING_ACTION):
            self._settings[const.SETTING_ACTION] = DEFAULT_SETTINGS.copy()
            self._action.set_settings(self._settings)

        self.load()

    def load(self) -> None:
        """
        Loads the settings from the action.
        :return: None
        """
        super().load()
        self._ha_action = self._settings[const.SETTING_ACTION][const.SETTING_ACTION]
        self._parameters = self._settings[const.SETTING_ACTION][const.ACTION_PARAMETERS]

    def get_action(self) -> str:
        """
        Get the action.
        :return: the action
        """
        return self._ha_action

    def get_parameters(self) -> Dict:
        """
        Retrieve all action parameters.
        :return: all action parameters
        """
        return self._parameters

    def set_action_parameter(self, field, value) -> None:
        """
        Set the action parameter for the field.
        :param field: the field to set
        :param value: the value for the field
        """
        self._settings[const.SETTING_ACTION][const.ACTION_PARAMETERS][field] = value
        self.load()
        self._action.set_settings(self._settings)

    def remove_action_parameter(self, field) -> None:
        """
        Remove the action parameter for the field.
        :param field: the field to remove
        """
        self._settings[const.SETTING_ACTION][const.ACTION_PARAMETERS].pop(field)
        self.load()
        self._action.set_settings(self._settings)

    def clear_action_parameters(self) -> None:
        """Clear all action parameters."""
        self._settings[const.SETTING_ACTION][const.ACTION_PARAMETERS] = {}
        self.load()
        self._action.set_settings(self._settings)

    def reset(self, domain: str) -> None:
        """
        Empty the settings and keep only the UUID and the given domain.
        :param domain: the new domain
        """
        super().reset(domain)
        self._settings[const.SETTING_ACTION][const.SETTING_ACTION] = const.EMPTY_STRING
        self._settings[const.SETTING_ACTION][const.ACTION_PARAMETERS] = {}
        self.load()
        self._action.set_settings(self._settings)
