"""Module to manage HomeAssistantPlugin action settings."""

import uuid

from de_gensyn_HomeAssistantPlugin.actions import const

DEFAULT_SETTINGS = {
    const.SETTING_DOMAIN: const.EMPTY_STRING,
    const.SETTING_ENTITY: const.EMPTY_STRING
}


class Settings:
    """
    Class to manage all settings for an HomeAssistantPlugin action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action):
        self._action = action

        self._domain = None
        self._entity = None

        self._settings = self._action.get_settings()

        if not self._settings.get(const.SETTING_ENTITY):
            self._settings[const.SETTING_ENTITY] = DEFAULT_SETTINGS.copy()
            self._action.set_settings(self._settings)

        Settings.load(self)

    def load(self) -> None:
        """
        Loads the settings from the action.
        :return: None
        """
        self._settings = self._action.get_settings()
        self._domain = self._settings[const.SETTING_ENTITY][const.SETTING_DOMAIN]
        self._entity = self._settings[const.SETTING_ENTITY][const.SETTING_ENTITY]

    def get_domain(self) -> str:
        """
        Get the domain.
        :return: the domain
        """
        return self._domain

    def get_entity(self) -> str:
        """
        Get the entity.
        :return: the entity
        """
        return self._entity

    def reset(self, domain: str) -> None:
        """
        Delete the settings and keeps only the UUID. The given domain is also set.
        :param domain: the new domain
        """
        self._settings[const.SETTING_ENTITY][const.SETTING_DOMAIN] = domain
        self._settings[const.SETTING_ENTITY][const.SETTING_ENTITY] = const.EMPTY_STRING
        self.load()
        self._action.set_settings(self._settings)
