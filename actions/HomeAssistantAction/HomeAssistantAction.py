# Import python modules
import io
import logging
from typing import Any

import cairosvg
# Import gtk modules - used for the config rows
import gi
from PIL import Image

from locales.LegacyLocaleManager import LegacyLocaleManager
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from plugins.de_gensyn_HomeAssistantPlugin.HomeAssistantActionBase import HomeAssistantActionBase
from plugins.de_gensyn_HomeAssistantPlugin.const import CONNECT_BIND, SETTING_ENTITY_ENTITY, SETTING_SERVICE_SERVICE_ON_KEY_DOWN, \
    SETTING_SERVICE_SERVICE_ON_KEY_UP, SETTING_SERVICE_SERVICE, LABEL_ENTITY_DOMAIN, LABEL_ENTITY_ENTITY, \
    LABEL_SERVICE_SERVICE, LABEL_SERVICE_CALL_ON_KEY_DOWN, LABEL_SETTINGS_ENTITY, LABEL_SERVICE_CALL_ON_KEY_UP, \
    LABEL_SETTINGS_SERVICE, LABEL_ICON_SHOW_ICON, LABEL_SETTINGS_ICON, SETTING_ICON_SHOW_ICON, CONNECT_NOTIFY_SELECTED, \
    CONNECT_NOTIFY_ACTIVE, SETTING_ENTITY_DOMAIN, EMPTY_STRING, ATTRIBUTE_FRIENDLY_NAME

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import Align, Label, SignalListItemFactory, StringList
from gi.repository.Adw import ComboRow, PreferencesGroup, SwitchRow


class HomeAssistantAction(HomeAssistantActionBase):
    lm: LegacyLocaleManager
    combo_factory: SignalListItemFactory

    domain_combo: ComboRow
    domain_model: StringList

    entity_combo: ComboRow
    entity_model: StringList

    service_combo: ComboRow
    service_model: StringList

    service_on_key_down: SwitchRow
    service_on_key_up: SwitchRow

    show_icon: SwitchRow

    def __init__(self, action_id: str, action_name: str,
                 deck_controller: DeckController, page: Page, coords: str, plugin_base: PluginBase, state: int):
        super().__init__(action_id=action_id, action_name=action_name,
                         deck_controller=deck_controller, page=page, coords=coords, plugin_base=plugin_base,
                         state=state)

    def on_ready(self) -> None:
        entity = self.get_setting(SETTING_ENTITY_ENTITY)

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, f"{self.page.json_path}{self.page_coords}",
                                                        self.entity_updated)

        self.entity_updated(entity)

    def on_key_down(self) -> None:
        if self.get_setting(SETTING_SERVICE_SERVICE_ON_KEY_DOWN, True):
            self.call_service()

    def on_key_up(self) -> None:
        if self.get_setting(SETTING_SERVICE_SERVICE_ON_KEY_UP, False):
            self.call_service()

    def call_service(self) -> None:
        settings = self.get_settings()
        entity = settings.get(SETTING_ENTITY_ENTITY)
        service = settings.get(SETTING_SERVICE_SERVICE)

        if not entity or not service:
            return

        self.plugin_base.backend.call_service(entity, service)

    def get_config_rows(self) -> list:
        self.lm = self.plugin_base.locale_manager

        rows: list = super().get_config_rows()

        self.combo_factory = SignalListItemFactory()
        self.combo_factory.connect(CONNECT_BIND, self._factory_bind)

        entity_group = self._get_entity_group()
        service_group = self._get_service_group()
        icon_group = self._get_icon_group()

        self.load_domains()

        self.set_enabled_disabled()

        # connect as the last action - else the on_change functions trigger on populating the models
        self._connect_rows()

        if self.plugin_base.backend.is_connected():
            # already connected to home assistant -> put global settings at the bottom
            return [entity_group, service_group, icon_group, *rows]

        return [*rows, entity_group, service_group, icon_group]

    def _get_entity_group(self) -> PreferencesGroup:
        self.domain_combo = ComboRow(title=self.lm.get(LABEL_ENTITY_DOMAIN))
        self.domain_combo.set_factory(self.combo_factory)

        self.entity_combo = ComboRow(title=self.lm.get(LABEL_ENTITY_ENTITY))
        self.entity_combo.set_factory(self.combo_factory)

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_ENTITY))
        group.set_margin_top(20)
        group.add(self.domain_combo)
        group.add(self.entity_combo)

        return group

    def _get_service_group(self) -> PreferencesGroup:
        self.service_combo = ComboRow(title=self.lm.get(LABEL_SERVICE_SERVICE))
        self.service_combo.set_factory(self.combo_factory)

        self.service_on_key_down = SwitchRow(
            title=self.lm.get(LABEL_SERVICE_CALL_ON_KEY_DOWN))
        self.service_on_key_down.set_active(self.get_setting(SETTING_SERVICE_SERVICE_ON_KEY_DOWN, True))

        self.service_on_key_up = SwitchRow(title=self.lm.get(LABEL_SERVICE_CALL_ON_KEY_UP))
        self.service_on_key_up.set_active(self.get_setting(SETTING_SERVICE_SERVICE_ON_KEY_UP, False))

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_SERVICE))
        group.set_margin_top(20)
        group.add(self.service_combo)
        group.add(self.service_on_key_down)
        group.add(self.service_on_key_up)

        return group

    def _get_icon_group(self) -> PreferencesGroup:
        self.show_icon = SwitchRow(title=self.lm.get(LABEL_ICON_SHOW_ICON))
        self.show_icon.set_active(self.get_setting(SETTING_ICON_SHOW_ICON, True))

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_ICON))
        group.set_margin_top(20)
        group.add(self.show_icon)

        return group

    def _connect_rows(self) -> None:
        self.domain_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_domain)
        self.entity_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_entity)
        self.service_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_service)
        self.service_on_key_down.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch,
                                         SETTING_SERVICE_SERVICE_ON_KEY_DOWN)
        self.service_on_key_up.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch, SETTING_SERVICE_SERVICE_ON_KEY_UP)
        self.show_icon.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch, SETTING_ICON_SHOW_ICON)

    def on_change_switch(self, switch, *args):
        settings = self.get_settings()
        settings[args[1]] = switch.get_active()
        self.set_settings(settings)

        if args[1] == SETTING_ICON_SHOW_ICON:
            self.entity_updated(settings.get(SETTING_ENTITY_ENTITY))

        self.set_enabled_disabled()

    def _factory_bind(self, _, item):
        label = Label(halign=Align.END)
        item.set_child(label)

        entity_id = item.get_item().get_string()

        friendly_name = self.plugin_base.backend.get_entity(entity_id).get(ATTRIBUTE_FRIENDLY_NAME, EMPTY_STRING)

        label.set_text(entity_id)
        label.set_tooltip_text(friendly_name if friendly_name else entity_id)

    def on_change_domain(self, combo, _):
        settings = self.get_settings()

        old_domain = settings.setdefault(SETTING_ENTITY_DOMAIN, EMPTY_STRING)

        domain = combo.get_selected_item().get_string()

        if old_domain != domain:
            settings[SETTING_ENTITY_DOMAIN] = domain
            settings[SETTING_ENTITY_ENTITY] = EMPTY_STRING
            settings[SETTING_SERVICE_SERVICE] = EMPTY_STRING
            self.set_settings(settings)

            self.entity_combo.set_model(None)
            self.service_combo.set_model(None)
            self.set_media(image=None)

        if domain:
            self.load_entities()
            self.load_services()

        self.set_enabled_disabled()

    def on_change_entity(self, combo, _):
        settings = self.get_settings()
        old_entity = settings[SETTING_ENTITY_ENTITY]
        entity = combo.get_selected_item().get_string()

        if old_entity == entity:
            return

        settings[SETTING_ENTITY_ENTITY] = entity
        self.set_settings(settings)

        if old_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, f"{self.page.json_path}{self.page_coords}")

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, f"{self.page.json_path}{self.page_coords}",
                                                        self.entity_updated)

        self.entity_updated(entity)

        self.set_enabled_disabled()

    def on_change_service(self, combo, _):
        service = combo.get_selected_item().get_string()
        settings = self.get_settings()
        settings[SETTING_SERVICE_SERVICE] = service
        self.set_settings(settings)

        self.set_enabled_disabled()

    def entity_updated(self, entity: str, icon_svg: str = EMPTY_STRING) -> None:
        settings = self.get_settings()

        if not entity or not settings.get(SETTING_ICON_SHOW_ICON):
            self.set_media(image=None)
            return

        settings_entity = settings.get(SETTING_ENTITY_ENTITY)

        if entity != settings_entity:
            logging.error(f"Mismatching entities; settings: {settings_entity}, callback: {entity}")

            return

        service = self.get_setting(SETTING_SERVICE_SERVICE)

        if not icon_svg:
            icon_svg = self.plugin_base.backend.get_icon(entity)

            if not icon_svg:
                return

        png_data = cairosvg.svg2png(bytestring=icon_svg, dpi=600)

        image = Image.open(io.BytesIO(png_data))

        self.set_media(image=image)

    def load_domains(self):
        old_domain = self.get_settings().get(SETTING_ENTITY_DOMAIN, EMPTY_STRING)

        self.domain_model = StringList.new([EMPTY_STRING])
        self.domain_combo.set_model(self.domain_model)

        domains = sorted(self.plugin_base.backend.get_domains())

        for domain in domains:
            self.domain_model.append(domain)

        if old_domain in domains:
            set_value_in_combo(self.domain_combo, self.domain_model, old_domain)
            self.load_entities()
            self.load_services()

    def load_entities(self):
        old_entity = self.get_settings().get(SETTING_ENTITY_ENTITY, EMPTY_STRING)

        self.entity_model = StringList.new([EMPTY_STRING])
        self.entity_combo.set_model(self.entity_model)

        entities = sorted(self.plugin_base.backend.get_entities(self.domain_combo.get_selected_item().get_string()))

        for entity in entities:
            self.entity_model.append(entity)

        set_value_in_combo(self.entity_combo, self.entity_model, old_entity)

    def load_services(self):
        old_service = self.get_settings().get(SETTING_SERVICE_SERVICE, EMPTY_STRING)

        self.service_model = StringList.new([EMPTY_STRING])
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

    def set_enabled_disabled(self) -> None:
        domain = self.domain_combo.get_selected_item().get_string() if self.domain_combo.get_selected_item() else False
        domain_enabled = bool(domain)
        self.entity_combo.set_sensitive(domain_enabled)
        self.service_combo.set_sensitive(domain_enabled)

        service = self.service_combo.get_selected_item().get_string() if self.service_combo.get_selected_item() else False
        service_enabled = bool(service)
        self.service_on_key_down.set_sensitive(service_enabled)
        self.service_on_key_up.set_sensitive(service_enabled)

        entity = self.entity_combo.get_selected_item().get_string() if self.entity_combo.get_selected_item() else False
        entity_enabled = bool(entity)
        self.show_icon.set_sensitive(entity_enabled)


def set_value_in_combo(combo: ComboRow, model: StringList, value: str):
    if not value:
        return

    for i in range(len(model)):
        if model.get_string(i) == value:
            combo.set_selected(i)
            return
