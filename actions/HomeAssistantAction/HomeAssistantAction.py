# Import python modules
import io
import logging
from typing import Any

import cairosvg
# Import gtk modules - used for the config rows
import gi
from PIL import Image
from plugins.de_gensyn_HomeAssistantPlugin.HomeAssistantActionBase import HomeAssistantActionBase
from plugins.de_gensyn_HomeAssistantPlugin.const import CONNECT_BIND, SETTING_ENTITY_ENTITY, \
    SETTING_SERVICE_SERVICE_ON_KEY_DOWN, SETTING_TEXT_SHOW_TEXT, TEXT_POSITION_TOP, TEXT_POSITION_CENTER, \
    TEXT_POSITION_BOTTOM, LABEL_TEXT_POSITION, LABEL_SETTINGS_TEXT, SETTING_TEXT_POSITION, SETTING_TEXT_SIZE, \
    SETTING_SERVICE_SERVICE_ON_KEY_UP, SETTING_SERVICE_SERVICE, LABEL_ENTITY_DOMAIN, LABEL_ENTITY_ENTITY, \
    LABEL_SERVICE_SERVICE, LABEL_SERVICE_CALL_ON_KEY_DOWN, LABEL_SETTINGS_ENTITY, LABEL_SERVICE_CALL_ON_KEY_UP, \
    LABEL_SETTINGS_SERVICE, LABEL_ICON_SHOW_ICON, LABEL_SETTINGS_ICON, SETTING_ICON_SHOW_ICON, CONNECT_NOTIFY_SELECTED, \
    CONNECT_NOTIFY_ACTIVE, SETTING_ENTITY_DOMAIN, EMPTY_STRING, ATTRIBUTE_FRIENDLY_NAME, LABEL_TEXT_SHOW_TEXT, \
    LABEL_TEXT_SIZE, LABEL_TEXT_SHOW_UNIT, SETTING_TEXT_SHOW_UNIT, LABEL_TEXT_UNIT_LINE_BREAK, \
    SETTING_TEXT_UNIT_LINE_BREAK, LABEL_TEXT_ATTRIBUTE, CONNECT_CHANGED, ATTRIBUTES, SETTING_TEXT_ATTRIBUTE, \
    LABEL_TEXT_ADAPTIVE_SIZE, SETTING_TEXT_ADAPTIVE_SIZE, ATTRIBUTE_UNIT_OF_MEASUREMENT, STATE

from locales.LegacyLocaleManager import LegacyLocaleManager
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import Align, Label, SignalListItemFactory, StringList
from gi.repository.Adw import ComboRow, PreferencesGroup, SpinRow, SwitchRow


class HomeAssistantAction(HomeAssistantActionBase):
    lm: LegacyLocaleManager
    combo_factory: SignalListItemFactory

    entity_domain_combo: ComboRow
    entity_domain_model: StringList

    entity_entity_combo: ComboRow
    entity_entity_model: StringList

    service_service_combo: ComboRow
    service_service_model: StringList

    service_call_on_key_down: SwitchRow
    service_call_on_key_up: SwitchRow

    icon_show_icon: SwitchRow

    text_show_text: SwitchRow
    text_position_combo: ComboRow
    text_position_model: StringList
    text_adaptive_size: SwitchRow
    text_size: SpinRow
    text_show_unit: SwitchRow
    text_unit_line_break: SwitchRow
    text_attribute_combo: ComboRow
    text_attribute_model: StringList

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
        text_group = self._get_text_group()

        self.load_domains()

        self.set_enabled_disabled()

        # connect as the last action - else the on_change functions trigger on populating the models
        self._connect_rows()

        if self.plugin_base.backend.is_connected():
            # already connected to home assistant -> put global settings at the bottom
            return [entity_group, service_group, icon_group, text_group, *rows]

        return [*rows, entity_group, service_group, icon_group, text_group]

    def _get_entity_group(self) -> PreferencesGroup:
        self.entity_domain_combo = ComboRow(title=self.lm.get(LABEL_ENTITY_DOMAIN))
        self.entity_domain_combo.set_factory(self.combo_factory)

        self.entity_entity_combo = ComboRow(title=self.lm.get(LABEL_ENTITY_ENTITY))
        self.entity_entity_combo.set_factory(self.combo_factory)

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_ENTITY))
        group.set_margin_top(20)
        group.add(self.entity_domain_combo)
        group.add(self.entity_entity_combo)

        return group

    def _get_service_group(self) -> PreferencesGroup:
        self.service_service_combo = ComboRow(title=self.lm.get(LABEL_SERVICE_SERVICE))
        self.service_service_combo.set_factory(self.combo_factory)

        self.service_call_on_key_down = SwitchRow(
            title=self.lm.get(LABEL_SERVICE_CALL_ON_KEY_DOWN))
        self.service_call_on_key_down.set_active(self.get_setting(SETTING_SERVICE_SERVICE_ON_KEY_DOWN, True))

        self.service_call_on_key_up = SwitchRow(title=self.lm.get(LABEL_SERVICE_CALL_ON_KEY_UP))
        self.service_call_on_key_up.set_active(self.get_setting(SETTING_SERVICE_SERVICE_ON_KEY_UP, False))

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_SERVICE))
        group.set_margin_top(20)
        group.add(self.service_service_combo)
        group.add(self.service_call_on_key_down)
        group.add(self.service_call_on_key_up)

        return group

    def _get_icon_group(self) -> PreferencesGroup:
        self.icon_show_icon = SwitchRow(title=self.lm.get(LABEL_ICON_SHOW_ICON))
        self.icon_show_icon.set_active(self.get_setting(SETTING_ICON_SHOW_ICON, False))

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_ICON))
        group.set_margin_top(20)
        group.add(self.icon_show_icon)

        return group

    def _get_text_group(self) -> PreferencesGroup:
        self.text_show_text = SwitchRow(title=self.lm.get(LABEL_TEXT_SHOW_TEXT))
        self.text_show_text.set_active(self.get_setting(SETTING_TEXT_SHOW_TEXT, False))

        self.text_position_model = StringList.new([TEXT_POSITION_TOP, TEXT_POSITION_CENTER, TEXT_POSITION_BOTTOM])

        self.text_position_combo = ComboRow(title=self.lm.get(LABEL_TEXT_POSITION))
        self.text_position_combo.set_factory(self.combo_factory)
        self.text_position_combo.set_model(self.text_position_model)

        set_value_in_combo(self.text_position_combo, self.text_position_model,
                           self.get_setting(SETTING_TEXT_POSITION, TEXT_POSITION_TOP))

        self.text_adaptive_size = SwitchRow(title=self.lm.get(LABEL_TEXT_ADAPTIVE_SIZE))
        self.text_adaptive_size.set_active(self.get_setting(SETTING_TEXT_ADAPTIVE_SIZE, True))

        self.text_size = SpinRow.new_with_range(0, 100, 1)
        self.text_size.set_title(self.lm.get(LABEL_TEXT_SIZE))
        self.text_size.set_value(self.get_setting(SETTING_TEXT_SIZE, 20))

        self.text_show_unit = SwitchRow(title=self.lm.get(LABEL_TEXT_SHOW_UNIT))
        self.text_show_unit.set_active(self.get_setting(SETTING_TEXT_SHOW_UNIT, False))

        self.text_unit_line_break = SwitchRow(title=self.lm.get(LABEL_TEXT_UNIT_LINE_BREAK))
        self.text_unit_line_break.set_active(self.get_setting(SETTING_TEXT_UNIT_LINE_BREAK, False))

        self.text_attribute_combo = ComboRow(title=self.lm.get(LABEL_TEXT_ATTRIBUTE))
        self.text_attribute_combo.set_factory(self.combo_factory)

        self.load_attributes()

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_TEXT))
        group.set_margin_top(20)
        group.add(self.text_show_text)
        group.add(self.text_position_combo)
        group.add(self.text_adaptive_size)
        group.add(self.text_size)
        group.add(self.text_show_unit)
        group.add(self.text_unit_line_break)
        group.add(self.text_attribute_combo)

        return group

    def _connect_rows(self) -> None:
        self.entity_domain_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_domain)
        self.entity_entity_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_entity)
        self.service_service_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_combo, SETTING_SERVICE_SERVICE)
        self.service_call_on_key_down.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch,
                                              SETTING_SERVICE_SERVICE_ON_KEY_DOWN)
        self.service_call_on_key_up.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch,
                                            SETTING_SERVICE_SERVICE_ON_KEY_UP)
        self.icon_show_icon.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch, SETTING_ICON_SHOW_ICON)
        self.text_show_text.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch, SETTING_TEXT_SHOW_TEXT)
        self.text_position_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_combo, SETTING_TEXT_POSITION)
        self.text_adaptive_size.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch, SETTING_TEXT_ADAPTIVE_SIZE)
        self.text_size.connect(CONNECT_CHANGED, self.on_change_size)
        self.text_show_unit.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch, SETTING_TEXT_SHOW_UNIT)
        self.text_unit_line_break.connect(CONNECT_NOTIFY_ACTIVE, self.on_change_switch, SETTING_TEXT_UNIT_LINE_BREAK)
        self.text_attribute_combo.connect(CONNECT_NOTIFY_SELECTED, self.on_change_combo, SETTING_TEXT_ATTRIBUTE)

    def on_change_switch(self, switch, *args):
        settings = self.get_settings()
        settings[args[1]] = switch.get_active()
        self.set_settings(settings)

        if args[1] == SETTING_ICON_SHOW_ICON:
            self.entity_updated(settings.get(SETTING_ENTITY_ENTITY))

        self.set_enabled_disabled()

        self.entity_updated(settings.get(SETTING_ENTITY_ENTITY))

    def _factory_bind(self, _, item):
        label = Label(halign=Align.END)
        item.set_child(label)

        entity_id = item.get_item().get_string()

        friendly_name = self.plugin_base.backend.get_entity(entity_id).get(ATTRIBUTES, {}).get(ATTRIBUTE_FRIENDLY_NAME,
                                                                                               EMPTY_STRING)

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

            self.entity_entity_combo.set_model(None)
            self.service_service_combo.set_model(None)
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

            self.load_attributes()

        self.entity_updated(entity)

        self.set_enabled_disabled()

    def on_change_combo(self, combo, *args):
        value = combo.get_selected_item().get_string()
        settings = self.get_settings()
        settings[args[1]] = value
        self.set_settings(settings)

        self.set_enabled_disabled()

        self.entity_updated(settings.get(SETTING_ENTITY_ENTITY))

    def on_change_size(self, spin):
        size = spin.get_value()
        settings = self.get_settings()
        settings[SETTING_TEXT_SIZE] = size
        self.set_settings(settings)

        self.entity_updated(settings.get(SETTING_ENTITY_ENTITY))

    def entity_updated(self, entity: str, state: dict = None, icon_svg: str = EMPTY_STRING) -> None:
        settings = self.get_settings()

        show_icon = settings.get(SETTING_ICON_SHOW_ICON)
        show_text = settings.get(SETTING_TEXT_SHOW_TEXT)

        if not entity or (not show_icon and not show_text):
            self.set_media(image=None)
            self.set_top_label(None)
            self.set_center_label(None)
            self.set_bottom_label(None)
            return

        settings_entity = settings.get(SETTING_ENTITY_ENTITY)

        if entity != settings_entity:
            logging.error(f"Mismatching entities; settings: {settings_entity}, callback: {entity}")

            return

        service = self.get_setting(SETTING_SERVICE_SERVICE)

        if show_icon:
            if not icon_svg:
                icon_svg = self.plugin_base.backend.get_icon(entity)

            if icon_svg:
                png_data = cairosvg.svg2png(bytestring=icon_svg, dpi=600)

                image = Image.open(io.BytesIO(png_data))

                self.set_media(image=image)
        else:
            self.set_media(image=None)

        if show_text:
            if not state:
                state = self.plugin_base.backend.get_entity(entity)

            if not state:
                self.set_top_label(None)
                self.set_center_label(None)
                self.set_bottom_label(None)
                return

            text = state.get(STATE)
            text_length = len(text)
            text_height = 1
            attribute = settings.get(SETTING_TEXT_ATTRIBUTE)

            if attribute:
                text = state.get(ATTRIBUTES, {}).get(attribute, EMPTY_STRING)
                text_length = len(text)
            else:
                if settings.get(SETTING_TEXT_SHOW_UNIT):
                    unit = state.get(ATTRIBUTES, {}).get(ATTRIBUTE_UNIT_OF_MEASUREMENT, EMPTY_STRING)

                    if settings.get(SETTING_TEXT_UNIT_LINE_BREAK):
                        text_length = max(len(text), len(unit))
                        text = f"{text}\n{unit}"
                        text_height = 2
                    else:
                        text = f"{text} {unit}"
                        text_length = len(text)

            position = settings.get(SETTING_TEXT_POSITION)
            font_size = settings.get(SETTING_TEXT_SIZE)

            if settings.get(SETTING_TEXT_ADAPTIVE_SIZE):
                if text_length == 1:
                    font_size = 50
                elif text_length == 2:
                    font_size = 40
                else:
                    font_size = 30 - 3*(text_length-3)

                if text_height > 1:
                    # account for text with line break
                    font_size = min(font_size, 35)

                # set minimal font size, smaller is not readable
                font_size = max(font_size, 10)

            if position == TEXT_POSITION_TOP:
                self.set_top_label(text, font_size=font_size)
                self.set_center_label(None)
                self.set_bottom_label(None)
            elif position == TEXT_POSITION_CENTER:
                self.set_top_label(None)
                self.set_center_label(text, font_size=font_size)
                self.set_bottom_label(None)
            elif position == TEXT_POSITION_BOTTOM:
                self.set_top_label(None)
                self.set_center_label(None)
                self.set_bottom_label(text, font_size=font_size)
        else:
            self.set_top_label(None)
            self.set_center_label(None)
            self.set_bottom_label(None)

    def load_domains(self):
        old_domain = self.get_settings().get(SETTING_ENTITY_DOMAIN, EMPTY_STRING)

        self.entity_domain_model = StringList.new([EMPTY_STRING])
        self.entity_domain_combo.set_model(self.entity_domain_model)

        domains = sorted(self.plugin_base.backend.get_domains())

        for domain in domains:
            self.entity_domain_model.append(domain)

        if old_domain in domains:
            set_value_in_combo(self.entity_domain_combo, self.entity_domain_model, old_domain)
            self.load_entities()
            self.load_services()

    def load_entities(self):
        old_entity = self.get_settings().get(SETTING_ENTITY_ENTITY, EMPTY_STRING)

        self.entity_entity_model = StringList.new([EMPTY_STRING])
        self.entity_entity_combo.set_model(self.entity_entity_model)

        entities = sorted(
            self.plugin_base.backend.get_entities(self.entity_domain_combo.get_selected_item().get_string()))

        for entity in entities:
            self.entity_entity_model.append(entity)

        set_value_in_combo(self.entity_entity_combo, self.entity_entity_model, old_entity)

    def load_services(self):
        old_service = self.get_settings().get(SETTING_SERVICE_SERVICE, EMPTY_STRING)

        self.service_service_model = StringList.new([EMPTY_STRING])
        self.service_service_combo.set_model(self.service_service_model)

        services = self.plugin_base.backend.get_services(self.entity_domain_combo.get_selected_item().get_string())

        for service in services:
            self.service_service_model.append(service)

        set_value_in_combo(self.service_service_combo, self.service_service_model, old_service)

    def load_attributes(self):
        old_attribute = self.get_settings().get(SETTING_TEXT_ATTRIBUTE, EMPTY_STRING)

        ha_entity = self.plugin_base.backend.get_entity(self.get_setting(SETTING_ENTITY_ENTITY))

        self.text_attribute_model = StringList.new([EMPTY_STRING])

        for attribute in ha_entity.get(ATTRIBUTES, {}).keys():
            self.text_attribute_model.append(attribute)

        self.text_attribute_combo.set_model(self.text_attribute_model)

        set_value_in_combo(self.text_attribute_combo, self.text_attribute_model, old_attribute)

    def get_setting(self, setting: str, default: Any = None) -> Any:
        settings = self.get_settings()
        value = settings.setdefault(setting, default)
        self.set_settings(settings)
        return value

    def set_enabled_disabled(self) -> None:
        domain = self.entity_domain_combo.get_selected_item().get_string() if self.entity_domain_combo.get_selected_item() else False
        domain_selected = bool(domain)
        self.entity_entity_combo.set_sensitive(domain_selected and len(self.entity_entity_model) > 1)
        self.service_service_combo.set_sensitive(domain_selected and len(self.service_service_model) > 1)

        service = self.service_service_combo.get_selected_item().get_string() if self.service_service_combo.get_selected_item() else False
        service_selected = bool(service)
        self.service_call_on_key_down.set_sensitive(service_selected)
        self.service_call_on_key_up.set_sensitive(service_selected)

        entity = self.entity_entity_combo.get_selected_item().get_string() if self.entity_entity_combo.get_selected_item() else False
        entity_enabled = bool(entity)
        self.icon_show_icon.set_sensitive(entity_enabled)
        self.text_show_text.set_sensitive(entity_enabled)

        if entity and self.text_show_text.get_active():
            ha_entity = self.plugin_base.backend.get_entity(self.get_setting(SETTING_ENTITY_ENTITY))

            self.text_position_combo.set_sensitive(True)
            self.text_adaptive_size.set_sensitive(True)
            self.text_size.set_sensitive(not self.text_adaptive_size.get_active())
            self.text_attribute_combo.set_sensitive(len(self.text_attribute_model) > 1)

            has_unit = bool(ha_entity.get(ATTRIBUTES, {}).get(ATTRIBUTE_UNIT_OF_MEASUREMENT, False))

            if not has_unit:
                self.text_show_unit.set_active(False)
                self.text_unit_line_break.set_active(False)

            attribute = self.text_attribute_combo.get_selected_item().get_string() if self.text_attribute_combo.get_selected_item() else False
            no_attribute_selected = not bool(attribute)

            unit_rows_active = has_unit and no_attribute_selected

            self.text_show_unit.set_sensitive(unit_rows_active)
            self.text_unit_line_break.set_sensitive(unit_rows_active)

            if not self.text_show_unit.get_active():
                self.text_unit_line_break.set_active(False)
                self.text_unit_line_break.set_sensitive(False)
        else:
            self.text_position_combo.set_sensitive(False)
            self.text_adaptive_size.set_sensitive(False)
            self.text_size.set_sensitive(False)
            self.text_attribute_combo.set_sensitive(False)
            self.text_show_unit.set_sensitive(False)
            self.text_unit_line_break.set_sensitive(False)


def set_value_in_combo(combo: ComboRow, model: StringList, value: str):
    if not value:
        return

    for i in range(len(model)):
        if model.get_string(i) == value:
            combo.set_selected(i)
            return
