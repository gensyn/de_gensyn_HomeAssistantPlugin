"""
Module for the Home Assistant action base class.
"""

import gi

from de_gensyn_HomeAssistantPlugin.const import (CONNECT_NOTIFY_TEXT, CONNECT_NOTIFY_ACTIVE,
                                                 LABEL_BASE_HOST, LABEL_BASE_PORT, LABEL_BASE_SSL,
                                                 LABEL_BASE_TOKEN, SETTING_HOST, SETTING_PORT,
                                                 SETTING_TOKEN, SETTING_SSL, CONNECTED,
                                                 NOT_CONNECTED, LABEL_BASE_SETTINGS,
                                                 LABEL_BASE_SETTINGS_HEADER)
from src.backend.PluginManager.ActionBase import ActionBase

gi.require_version("Adw", "1")
from gi.repository.Adw import EntryRow, ExpanderRow, PasswordEntryRow, PreferencesGroup, SwitchRow


class HomeAssistantActionBase(ActionBase):
    """
    Base class for the Home Assistant action, managing credentials.
    """
    host_entry: EntryRow
    port_entry: EntryRow
    ssl_switch: SwitchRow
    token_entry: PasswordEntryRow
    connection_status: EntryRow
    settings_expander: ExpanderRow

    def get_config_rows(self) -> list:
        """
        Gets the rows for configuring Home Assistant credentials and base settings.
        """
        lm = self.plugin_base.locale_manager

        self.host_entry = EntryRow(title=lm.get(LABEL_BASE_HOST))
        self.port_entry = EntryRow(title=lm.get(LABEL_BASE_PORT))
        self.ssl_switch = SwitchRow(title=lm.get(LABEL_BASE_SSL))
        self.token_entry = PasswordEntryRow(title=lm.get(LABEL_BASE_TOKEN))

        self.connection_status = EntryRow(title="Connection status:")
        self.connection_status.set_editable(False)
        self.connection_status.set_text(
            CONNECTED if self.plugin_base.backend.is_connected() else NOT_CONNECTED)

        self.plugin_base.backend.set_connection_status_callback(self._set_status)

        self._load_config_defaults_base()

        self.host_entry.connect(CONNECT_NOTIFY_TEXT, self._on_change_entry, SETTING_HOST)
        self.port_entry.connect(CONNECT_NOTIFY_TEXT, self._on_change_entry, SETTING_PORT)
        self.ssl_switch.connect(CONNECT_NOTIFY_ACTIVE, self._on_change_ssl)
        self.token_entry.connect(CONNECT_NOTIFY_TEXT, self._on_change_entry, SETTING_TOKEN)

        self.settings_expander = ExpanderRow(title=lm.get(LABEL_BASE_SETTINGS))
        self.settings_expander.add_row(self.host_entry)
        self.settings_expander.add_row(self.port_entry)
        self.settings_expander.add_row(self.ssl_switch)
        self.settings_expander.add_row(self.token_entry)

        group = PreferencesGroup()
        group.set_title(lm.get(LABEL_BASE_SETTINGS_HEADER))
        group.set_margin_top(20)
        group.add(self.settings_expander)
        group.add(self.connection_status)

        return [group]

    def _load_config_defaults_base(self) -> None:
        """
        Loads Home Assistant base settings from the disk.
        """
        settings = self.plugin_base.get_settings()
        host = settings.get(SETTING_HOST, "")
        port = settings.get(SETTING_PORT, "")
        ssl = settings.get(SETTING_SSL, True)
        token = settings.get(SETTING_TOKEN, "")

        self.host_entry.set_text(host)
        self.port_entry.set_text(port)
        self.ssl_switch.set_active(ssl)
        self.token_entry.set_text(token)

    def _on_change_entry(self, entry, *args) -> None:
        """
        Executed when an entry row is changed.
        """
        settings = self.plugin_base.get_settings()
        settings[args[1]] = entry.get_text()
        self.plugin_base.set_settings(settings)

    def _on_change_ssl(self, switch, _) -> None:
        """
        Executed when a switch row is changed.
        """
        settings = self.plugin_base.get_settings()
        settings[SETTING_SSL] = bool(switch.get_active())
        self.plugin_base.set_settings(settings)

    def _set_status(self, status) -> None:
        """
        Callback function to be executed when the Home Assistant connection status changes.
        """
        self.connection_status.set_text(status)
        self.settings_expander.set_expanded(status != CONNECTED)
