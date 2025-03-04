"""
Entry point for StreamController to load the plugin.
"""
import sys
from pathlib import Path
from typing import Dict, Any

import gi
gi.require_version("Adw", "1")
from gi.repository import GLib
from gi.repository.Adw import EntryRow, SwitchRow, PasswordEntryRow, PreferencesGroup

ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase

from de_gensyn_HomeAssistantPlugin import const

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.home_asistant_action import \
    HomeAssistantAction
from de_gensyn_HomeAssistantPlugin.backend.home_assistant import HomeAssistantBackend


class HomeAssistant(PluginBase):  # pylint: disable=too-few-public-methods
    """
    The plugin class to be loaded by Stream Controller. Manages the credentials.
    """
    host_entry: EntryRow
    port_entry: EntryRow
    ssl_switch: SwitchRow
    verify_certificate_switch: SwitchRow
    token_entry: PasswordEntryRow
    connection_status: EntryRow

    def __init__(self):
        super().__init__()

        self.home_assistant_action_holder = ActionHolder(
            plugin_base=self,
            action_base=HomeAssistantAction,
            action_id="de_gensyn_HomeAssistantPlugin::HomeAssistantAction",
            action_name=const.HOME_ASSISTANT,
        )
        self.add_action_holder(self.home_assistant_action_holder)

        self.register(
            plugin_name=const.HOME_ASSISTANT,
            github_repo="https://github.com/gensyn/de_gensyn_HomeAssistantPlugin",
            plugin_version="0.9.7-beta",
            app_version="1.5.0-beta"
        )

        settings = self.get_settings()
        host = settings.get(const.SETTING_HOST, const.EMPTY_STRING)
        port = settings.get(const.SETTING_PORT, const.EMPTY_STRING)
        ssl = settings.get(const.SETTING_SSL, True)
        verify_certificate = settings.get(const.SETTING_VERIFY_CERTIFICATE, True)
        token = settings.get(const.SETTING_TOKEN, const.EMPTY_STRING)

        self.backend = HomeAssistantBackend()
        self.backend.set_host(host)
        self.backend.set_port(port)
        self.backend.set_ssl(ssl)
        self.backend.set_verify_certificate(verify_certificate)
        self.backend.set_token(token)

    def set_settings(self, settings: Dict[str, Any]):
        """
        Saves the settings to the disk.
        """
        super().set_settings(settings)

        host = settings.get(const.SETTING_HOST, const.EMPTY_STRING)
        port = settings.get(const.SETTING_PORT, const.EMPTY_STRING)
        ssl = settings.get(const.SETTING_SSL, True)
        verify_certificate = settings.get(const.SETTING_VERIFY_CERTIFICATE, True)
        token = settings.get(const.SETTING_TOKEN, const.EMPTY_STRING)

        self.backend.set_host(host)
        self.backend.set_port(port)
        self.backend.set_ssl(ssl)
        self.backend.set_verify_certificate(verify_certificate)
        self.backend.set_token(token)

    def get_settings_area(self):
        """
        Gets the rows for configuring Home Assistant credentials and base settings.
        """
        self.host_entry = EntryRow(title=self.locale_manager.get(const.LABEL_BASE_HOST))
        self.port_entry = EntryRow(title=self.locale_manager.get(const.LABEL_BASE_PORT))
        self.ssl_switch = SwitchRow(title=self.locale_manager.get(const.LABEL_BASE_SSL))
        self.verify_certificate_switch = SwitchRow(
            title=self.locale_manager.get(const.LABEL_BASE_VERIFY_CERTIFICATE))
        self.token_entry = PasswordEntryRow(title=self.locale_manager.get(const.LABEL_BASE_TOKEN))

        self.connection_status = EntryRow(title="Connection status:")
        self.connection_status.set_editable(False)
        self.connection_status.set_text(
            const.CONNECTED if self.backend.is_connected() else const.NOT_CONNECTED)

        self.backend.set_connection_status_callback(self.set_status)

        self._load_config_defaults_base()

        self.host_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                const.SETTING_HOST)
        self.port_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                const.SETTING_PORT)
        self.ssl_switch.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_base_switch,
                                const.SETTING_SSL)
        self.verify_certificate_switch.connect(const.CONNECT_NOTIFY_ACTIVE,
                                               self._on_change_base_switch,
                                               const.SETTING_VERIFY_CERTIFICATE)
        self.token_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                 const.SETTING_TOKEN)

        group = PreferencesGroup()
        group.set_title(self.locale_manager.get(const.LABEL_BASE_SETTINGS_HEADER))
        group.set_margin_top(20)
        group.add(self.host_entry)
        group.add(self.port_entry)
        group.add(self.ssl_switch)
        group.add(self.verify_certificate_switch)
        group.add(self.token_entry)
        group.add(self.connection_status)

        return group

    def _load_config_defaults_base(self) -> None:
        """
        Loads Home Assistant base settings from the disk.
        """
        settings = self.get_settings()
        host = settings.get(const.SETTING_HOST, "")
        port = settings.get(const.SETTING_PORT, "")
        ssl = settings.get(const.SETTING_SSL, True)
        verify_certificate = settings.get(const.SETTING_VERIFY_CERTIFICATE, True)
        token = settings.get(const.SETTING_TOKEN, "")

        self.host_entry.set_text(host)
        self.port_entry.set_text(port)
        self.ssl_switch.set_active(ssl)
        self.verify_certificate_switch.set_active(verify_certificate)
        self.token_entry.set_text(token)

    def _on_change_base_entry(self, entry, *args) -> None:
        """
        Executed when an entry row is changed.
        """
        settings = self.get_settings()
        settings[args[1]] = entry.get_text()
        self.set_settings(settings)

    def _on_change_base_switch(self, switch, *args) -> None:
        """
        Executed when a switch row is changed.
        """
        settings = self.get_settings()
        settings[args[1]] = bool(switch.get_active())

        if args[1] == const.SETTING_SSL and bool(switch.get_active()):
            self.verify_certificate_switch.set_active(
                settings.get(const.SETTING_VERIFY_CERTIFICATE, True))
            self.verify_certificate_switch.set_sensitive(True)
        elif args[1] == const.SETTING_SSL:
            self.verify_certificate_switch.set_active(False)
            self.verify_certificate_switch.set_sensitive(False)

        self.set_settings(settings)

    def set_status(self, status) -> None:
        """
        Callback function to be executed when the Home Assistant connection status changes.
        """
        GLib.idle_add(self.connection_status.set_text, status)
