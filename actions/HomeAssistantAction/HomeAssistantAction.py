# Import python modules
import io
import logging
from typing import Any

import cairosvg
# Import gtk modules - used for the config rows
import gi
from PIL import Image

from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from ...HomeAssistant import CONNECTED
from ...HomeAssistantActionBase import HomeAssistantActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import StringList
from gi.repository.Adw import ComboRow, PreferencesGroup, SwitchRow


class HomeAssistantAction(HomeAssistantActionBase):
    domain_combo: ComboRow
    domain_model: StringList

    entity_combo: ComboRow
    entity_model: StringList

    service_combo: ComboRow
    service_model: StringList

    execute_on_key_down: SwitchRow
    execute_on_key_up: SwitchRow

    def __init__(self, action_id: str, action_name: str,
                 deck_controller: DeckController, page: Page, coords: str, plugin_base: PluginBase):
        super().__init__(action_id=action_id, action_name=action_name,
                         deck_controller=deck_controller, page=page, coords=coords, plugin_base=plugin_base)

    def on_ready(self) -> None:
        entity = self.get_setting("entity")

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, f"{self.page.json_path}{self.page_coords}",
                                                        self.entity_updated)

        self.entity_updated(entity)

    def on_key_down(self) -> None:
        if self.get_setting("execute_on_key_down", True):
            self.call_service()

    def on_key_up(self) -> None:
        if self.get_setting("execute_on_key_up", False):
            self.call_service()

    def call_service(self) -> None:
        settings = self.get_settings()
        entity = settings.get("entity")
        service = settings.get("service")

        if not entity or not service:
            return

        self.plugin_base.backend.call_service(entity, service)

    def get_config_rows(self) -> list:
        lm = self.plugin_base.locale_manager

        rows: list = super().get_config_rows()

        self.domain_combo = ComboRow(title=lm.get("actions.home_assistant.domain.label"))

        self.entity_combo = ComboRow(title=lm.get("actions.home_assistant.entity.label"))
        self.entity_combo.set_sensitive(False)

        # entity_factory = SignalListItemFactory()
        # entity_factory.connect('setup', self._entity_factory_setup)
        # entity_factory.connect('bind', self._entity_factory_bind)
        # self.entity_combo.set_factory(entity_factory)

        self.service_combo = ComboRow(title=lm.get("actions.home_assistant.service.label"))
        self.service_combo.set_sensitive(False)

        self.execute_on_key_down = SwitchRow(title=lm.get("actions.home_assistant.execute_on_key_down.label"))
        self.execute_on_key_down.set_active(self.get_setting("execute_on_key_down", True))

        self.execute_on_key_up = SwitchRow(title=lm.get("actions.home_assistant.execute_on_key_up.label"))
        self.execute_on_key_up.set_active(self.get_setting("execute_on_key_up", False))

        group = PreferencesGroup()
        group.set_title(lm.get("actions.home_assistant.button_settings.label"))
        group.set_margin_top(20)
        group.add(self.domain_combo)
        group.add(self.entity_combo)
        group.add(self.service_combo)
        group.add(self.execute_on_key_down)
        group.add(self.execute_on_key_up)

        self.load_domains()

        self.domain_combo.connect("notify::selected", self.on_change_domain)
        self.entity_combo.connect("notify::selected", self.on_change_entity)
        self.service_combo.connect("notify::selected", self.on_change_service)

        self.execute_on_key_down.connect("notify::active", self.on_change_switch, "execute_on_key_down")
        self.execute_on_key_up.connect("notify::active", self.on_change_switch, "execute_on_key_up")

        if self.plugin_base.backend.get_connection_state() == CONNECTED:
            # already connected to home assistant -> put global settings at the bottom
            return [group, *rows]

        return [*rows, group]

    def on_change_switch(self, switch, *args):
        settings = self.get_settings()
        settings[args[1]] = switch.get_active()
        self.set_settings(settings)

    # def _entity_factory_setup(self, factory, item):
    #     label = Label(halign=Align.END)
    #     item.set_child(label)
    #
    # def _entity_factory_bind(self, factory, item):
    #     label = item.get_child()
    #
    #     entity_id = item.get_item().get_string()
    #
    #     friendly_name = self.plugin_base.backend.get_entity(entity_id).get("friendly_name", "")
    #
    #     label.set_label(f"{item.get_item().get_string()}" + f" ({friendly_name})" if friendly_name else "")

    def on_change_domain(self, combo, *args):
        settings = self.get_settings()

        domain = combo.get_selected_item().get_string()

        settings["domain"] = domain
        settings["entity"] = ""
        settings["service"] = ""
        self.set_settings(settings)

        self.load_entities()
        self.load_services()

        if not domain:
            self.entity_combo.set_sensitive(False)
            self.service_combo.set_sensitive(False)

    def on_change_entity(self, combo, *args):
        settings = self.get_settings()
        old_entity = settings["entity"]
        entity = combo.get_selected_item().get_string()

        if old_entity == entity:
            return

        settings["entity"] = entity
        self.set_settings(settings)

        if old_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, f"{self.page.json_path}{self.page_coords}")

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, f"{self.page.json_path}{self.page_coords}",
                                                        self.entity_updated)
            self.entity_updated(entity)

    def entity_updated(self, entity: str, icon_svg: str = ""):
        settings = self.get_settings()
        settings_entity = settings.get("entity")

        if entity != settings_entity:
            logging.error(f"Mismatching entities; settings: {settings_entity}, callback: {entity}")

            return

        service = self.get_setting("service")

        if not icon_svg:
            icon_svg = self.plugin_base.backend.get_icon(entity)

            if not icon_svg:
                return

        png_data = cairosvg.svg2png(bytestring=icon_svg, dpi=600)

        image = Image.open(io.BytesIO(png_data))

        self.set_media(image=image)

    def on_change_service(self, combo, *args):
        settings = self.get_settings()
        settings["service"] = combo.get_selected_item().get_string()
        self.set_settings(settings)

    def load_domains(self):
        old_domain = self.get_settings().get("domain", "")

        self.domain_model = StringList.new([""])
        self.domain_combo.set_model(self.domain_model)

        domains = sorted(self.plugin_base.backend.get_domains())

        for domain in domains:
            self.domain_model.append(domain)

        if old_domain in domains:
            set_value_in_combo(self.domain_combo, self.domain_model, old_domain)
            self.load_entities()
            self.load_services()

    def load_entities(self):
        old_entity = self.get_settings().get("entity", "")

        self.entity_combo.set_sensitive(True)
        self.entity_model = StringList.new([""])
        self.entity_combo.set_model(self.entity_model)

        entities = sorted(self.plugin_base.backend.get_entities(self.domain_combo.get_selected_item().get_string()))

        for entity in entities:
            self.entity_model.append(entity)

        set_value_in_combo(self.entity_combo, self.entity_model, old_entity)

    def load_services(self):
        old_service = self.get_settings().get("service", "")

        self.service_combo.set_sensitive(True)
        self.service_model = StringList.new([""])
        self.service_combo.set_model(self.service_model)

        services = self.plugin_base.backend.get_services(self.domain_combo.get_selected_item().get_string())

        for service in services:
            self.service_model.append(service)

        set_value_in_combo(self.service_combo, self.service_model, old_service)

    def get_setting(self, setting: str, default: Any = None) -> Any:
        settings = self.get_settings()
        value = settings.setdefault(setting, default)
        self.set_settings(settings)
        return value


def set_value_in_combo(combo: ComboRow, model: StringList, value: str):
    if not value:
        return

    for i in range(len(model)):
        if model.get_string(i) == value:
            combo.set_selected(i)
            return
