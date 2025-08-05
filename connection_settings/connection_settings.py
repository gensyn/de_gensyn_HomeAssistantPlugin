"""Module to manage Home Assistant connection action settings."""
from typing import Optional

from de_gensyn_HomeAssistantPlugin import const as base_const

class ConnectionSettings:
    """
    Class to manage connection settings for Home Assistant.
    :param hass: the Plugin main instance whose settings are being managed
    """

    def __init__(self, hass: "HomeAssistant"):
        self._hass = hass

        self._host: Optional[str] = None
        self._port: Optional[str] = None
        self._ssl: Optional[bool] = None
        self._verify_certificate: Optional[bool] = None
        self._token: Optional[str] = None

        self._settings = self._hass.get_settings()
        self._load_settings()

    def _load_settings(self) -> None:
        """
        Loads the settings from the instance.
        :return: None
        """
        self._host = self._settings.get(base_const.SETTING_HOST, base_const.EMPTY_STRING)
        self._port = self._settings.get(base_const.SETTING_PORT, base_const.EMPTY_STRING)
        self._ssl = self._settings.get(base_const.SETTING_SSL, True)
        self._verify_certificate = self._settings.get(base_const.SETTING_VERIFY_CERTIFICATE, True)
        self._token = self._settings.get(base_const.SETTING_TOKEN, base_const.EMPTY_STRING)

    def get_host(self) -> str:
        """
        Get the host.
        :return: the host
        """
        return self._host

    def get_port(self) -> str:
        """
        Get the port.
        :return: the port
        """
        return self._port

    def get_ssl(self) -> bool:
        """
        Get whether to use SSL.
        :return: whether to use SSL
        """
        return self._ssl

    def get_verify_certificate(self) -> bool:
        """
        Get whether to verify the certificate.
        :return: whether to verify the certificate
        """
        return self._verify_certificate

    def get_token(self) -> str:
        """
        Get the token.
        :return: the token
        """
        return self._token

    def set_setting(self, key, value) -> None:
        """Sets the setting in the local copy and also writes it to the disk."""
        self._settings[key] = value
        self._load_settings()
        self._hass.reload_settings()
        self._hass.set_settings(self._settings)
