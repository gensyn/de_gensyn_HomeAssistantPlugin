# Import gtk modules
import gi

from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Adw import EntryRow, PasswordEntryRow, PreferencesGroup, SpinRow, SwitchRow


class HomeAssistantActionBase(ActionBase):
    host_entry: EntryRow
    port_entry: EntryRow
    ssl_switch: SwitchRow
    token_entry: PasswordEntryRow

    def __init__(self, action_id: str, action_name: str,
                 deck_controller: "DeckController", page: Page, coords: str, plugin_base: PluginBase):
        super().__init__(action_id=action_id, action_name=action_name,
                         deck_controller=deck_controller, page=page, coords=coords, plugin_base=plugin_base)

    def get_config_rows(self) -> list:
        lm = self.plugin_base.locale_manager

        self.host_entry = EntryRow(title=lm.get("actions.base.host.label"))

        self.port_entry = EntryRow(title=lm.get("actions.base.port.label"))

        self.ssl_switch = SwitchRow(title=lm.get("actions.base.ssl.label"))

        self.token_entry = PasswordEntryRow(title=lm.get("actions.base.token.label"))

        self.load_config_defaults_base()

        self.host_entry.connect("notify::text", self.on_change_entry, "host")
        self.port_entry.connect("notify::text", self.on_change_entry, "port")
        self.ssl_switch.connect("notify::active", self.on_change_ssl)
        self.token_entry.connect("notify::text", self.on_change_entry, "token")

        group = PreferencesGroup()
        group.set_title(lm.get("actions.base.global_settings.label"))
        group.set_margin_top(20)
        group.add(self.host_entry)
        group.add(self.port_entry)
        group.add(self.ssl_switch)
        group.add(self.token_entry)

        return [group]

    def load_config_defaults_base(self):
        settings = self.plugin_base.get_settings()
        host = settings.setdefault("host", "")
        port = settings.setdefault("port", "")
        ssl = settings.setdefault("ssl", True)
        token = settings.setdefault("token", "")

        self.host_entry.set_text(host)
        self.port_entry.set_text(port)
        self.ssl_switch.set_active(ssl)
        self.token_entry.set_text(token)

    def on_change_entry(self, entry, *args):
        settings = self.plugin_base.get_settings()
        settings[args[1]] = entry.get_text()
        self.plugin_base.set_settings(settings)

    def on_change_ssl(self, switch, *args):
        settings = self.plugin_base.get_settings()
        settings["ssl"] = bool(switch.get_active())
        self.plugin_base.set_settings(settings)
