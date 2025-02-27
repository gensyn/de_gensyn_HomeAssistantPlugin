"""
Module for the Home Assistant action base class.
"""

import gi

from src.backend.PluginManager.ActionBase import ActionBase

gi.require_version("Adw", "1")
from gi.repository.Adw import EntryRow, ExpanderRow, PasswordEntryRow, PreferencesGroup, SwitchRow
from gi.repository import GLib

from de_gensyn_HomeAssistantPlugin import const


class HomeAssistantActionBase(ActionBase):
    """
    Base class for the Home Assistant action, managing credentials.
    """
    host_entry: EntryRow
    port_entry: EntryRow
    ssl_switch: SwitchRow
    verify_certificate_switch: SwitchRow
    token_entry: PasswordEntryRow
    connection_status: EntryRow
    settings_expander: ExpanderRow

    def get_config_rows(self) -> list:
        """
        Gets the rows for configuring Home Assistant credentials and base settings.
        """
        lm = self.plugin_base.locale_manager

        self.host_entry = EntryRow(title=lm.get(const.LABEL_BASE_HOST))
        self.port_entry = EntryRow(title=lm.get(const.LABEL_BASE_PORT))
        self.ssl_switch = SwitchRow(title=lm.get(const.LABEL_BASE_SSL))
        self.verify_certificate_switch = SwitchRow(
            title=lm.get(const.LABEL_BASE_VERIFY_CERTIFICATE))
        self.token_entry = PasswordEntryRow(title=lm.get(const.LABEL_BASE_TOKEN))

        self.connection_status = EntryRow(title="Connection status:")
        self.connection_status.set_editable(False)
        self.connection_status.set_text(
            const.CONNECTED if self.plugin_base.backend.is_connected() else const.NOT_CONNECTED)

        self.plugin_base.backend.set_connection_status_callback(self.set_status)

        self._load_config_defaults_base()

        self.host_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                const.SETTING_HOST)
        self.port_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                const.SETTING_PORT)
        self.ssl_switch.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_base_switch, const.SETTING_SSL)
        self.verify_certificate_switch.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_base_switch,
                                               const.SETTING_VERIFY_CERTIFICATE)
        self.token_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                 const.SETTING_TOKEN)

        self.settings_expander = ExpanderRow(title=lm.get(const.LABEL_BASE_SETTINGS))
        self.settings_expander.add_row(self.host_entry)
        self.settings_expander.add_row(self.port_entry)
        self.settings_expander.add_row(self.ssl_switch)
        self.settings_expander.add_row(self.verify_certificate_switch)
        self.settings_expander.add_row(self.token_entry)

        group = PreferencesGroup()
        group.set_title(lm.get(const.LABEL_BASE_SETTINGS_HEADER))
        group.set_margin_top(20)
        group.add(self.settings_expander)
        group.add(self.connection_status)

        return [group]

    def _load_config_defaults_base(self) -> None:
        """
        Loads Home Assistant base settings from the disk.
        """
        settings = self.plugin_base.get_settings()
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
        settings = self.plugin_base.get_settings()
        settings[args[1]] = entry.get_text()
        self.plugin_base.set_settings(settings)

    def _on_change_base_switch(self, switch, *args) -> None:
        """
        Executed when a switch row is changed.
        """
        settings = self.plugin_base.get_settings()
        settings[args[1]] = bool(switch.get_active())

        if args[1] == const.SETTING_SSL and bool(switch.get_active()):
            self.verify_certificate_switch.set_active(settings.get(const.SETTING_VERIFY_CERTIFICATE, True))
            self.verify_certificate_switch.set_sensitive(True)
        elif args[1] == const.SETTING_SSL:
            self.verify_certificate_switch.set_active(False)
            self.verify_certificate_switch.set_sensitive(False)


        self.plugin_base.set_settings(settings)


    def set_status(self, status) -> None:
        """
        Callback function to be executed when the Home Assistant connection status changes.
        """
        GLib.idle_add(self.connection_status.set_text, status)
        GLib.idle_add(self.settings_expander.set_expanded, status != const.CONNECTED)
