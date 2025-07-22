"""
Entry point for StreamController to load the plugin.
"""
import sys
from pathlib import Path

import gi

gi.require_version("Adw", "1")
from gi.repository import GLib
from gi.repository.Adw import EntryRow, SwitchRow, PasswordEntryRow, PreferencesGroup

ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.const import HOME_ASSISTANT_ACTION
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.const import PERFORM_ACTION
from de_gensyn_HomeAssistantPlugin.backend import const as backend_const

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.home_assistant_action import HomeAssistantAction
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.perform_action import PerformAction
from de_gensyn_HomeAssistantPlugin.backend.home_assistant import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.connection_settings.connection_settings import ConnectionSettings


class HomeAssistant(PluginBase):  # pylint: disable=too-few-public-methods
    """The plugin class to be loaded by Stream Controller. Manages the credentials."""
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
            action_name=HOME_ASSISTANT_ACTION,
        )

        self.service_action_holder = ActionHolder(
            plugin_base=self,
            action_base=PerformAction,
            action_id="de_gensyn_HomeAssistantPlugin::PerformAction",
            action_name=PERFORM_ACTION,
        )
        self.add_action_holder(self.home_assistant_action_holder)
        self.add_action_holder(self.service_action_holder)

        self.register(
            plugin_name=const.HOME_ASSISTANT,
            github_repo="https://github.com/gensyn/de_gensyn_HomeAssistantPlugin",
            plugin_version="1.0.3",
            app_version="1.5.0-beta"
        )

        self.connection = ConnectionSettings(self)
        host = self.connection.get_host()
        port = self.connection.get_port()
        ssl = self.connection.get_ssl()
        verify_certificate = self.connection.get_verify_certificate()
        token = self.connection.get_token()

        self.backend = HomeAssistantBackend(host, port, ssl, verify_certificate, token)

    def reload_settings(self):
        """Reconnects to Home Assistant with the new connection."""
        self.backend.set_host(self.connection.get_host())
        self.backend.set_port(self.connection.get_port())
        self.backend.set_ssl(self.connection.get_ssl())
        self.backend.set_verify_certificate(self.connection.get_verify_certificate())
        self.backend.set_token(self.connection.get_token())
        self.backend.reconnect()

    def get_settings_area(self):
        """Gets the rows for configuring Home Assistant credentials and base connection."""
        self.host_entry = EntryRow(title=self.locale_manager.get(const.LABEL_HOST))
        self.host_entry.set_text(self.connection.get_host())

        self.port_entry = EntryRow(title=self.locale_manager.get(const.LABEL_PORT))
        self.port_entry.set_text(self.connection.get_port())

        self.ssl_switch = SwitchRow(title=self.locale_manager.get(const.LABEL_SSL))
        self.ssl_switch.set_active(self.connection.get_ssl())

        self.verify_certificate_switch = SwitchRow(
            title=self.locale_manager.get(const.LABEL_VERIFY_CERTIFICATE))
        self.verify_certificate_switch.set_active(self.connection.get_verify_certificate())

        self.token_entry = PasswordEntryRow(title=self.locale_manager.get(const.LABEL_TOKEN))
        self.token_entry.set_text(self.connection.get_token())

        self.connection_status = EntryRow(title="Connection status:")
        self.connection_status.set_editable(False)
        self.connection_status.set_text(
            backend_const.CONNECTED if self.backend.is_connected() else backend_const.NOT_CONNECTED)

        self.backend.set_connection_status_callback(self.set_status)

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
        group.add(self.host_entry)
        group.add(self.port_entry)
        group.add(self.ssl_switch)
        group.add(self.verify_certificate_switch)
        group.add(self.token_entry)
        group.add(self.connection_status)

        return group

    def _on_change_base_entry(self, entry, *args) -> None:
        """Executed when an entry row is changed."""
        self.connection.set_setting(args[1], entry.get_text())

    def _on_change_base_switch(self, switch, *args) -> None:
        """Executed when a switch row is changed."""
        self.connection.set_setting(args[1], switch.get_active())

        if args[1] == const.SETTING_SSL and switch.get_active():
            self.verify_certificate_switch.set_sensitive(True)
            self.verify_certificate_switch.set_active(self.connection.get_verify_certificate())
        elif args[1] == const.SETTING_SSL:
            self.verify_certificate_switch.set_sensitive(False)
            self.verify_certificate_switch.set_active(False)

    def set_status(self, status) -> None:
        """Callback function to be executed when the Home Assistant connection status changes."""
        GLib.idle_add(self.connection_status.set_text, status)
