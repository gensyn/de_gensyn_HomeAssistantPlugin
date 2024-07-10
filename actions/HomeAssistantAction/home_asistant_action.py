"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import io
import json
import logging
import os
import uuid
from json import JSONDecodeError
from typing import Any, Dict

import cairosvg
import gi
# Import gtk modules - used for the config rows
from PIL import Image

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import Align, Label, SignalListItemFactory, StringList
from gi.repository.Adw import ComboRow, EntryRow, ExpanderRow, PreferencesGroup, SpinRow, SwitchRow

from plugins.de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import migration
from plugins.de_gensyn_HomeAssistantPlugin.home_assistant_action_base import HomeAssistantActionBase
from plugins.de_gensyn_HomeAssistantPlugin.const import (CONNECT_BIND, SETTING_ENTITY_ENTITY,
                                                         SETTING_TEXT_SHOW_TEXT, TEXT_POSITION_TOP,
                                                         TEXT_POSITION_CENTER,
                                                         TEXT_POSITION_BOTTOM,
                                                         LABEL_TEXT_POSITION, LABEL_SETTINGS_TEXT,
                                                         SETTING_TEXT_POSITION, SETTING_TEXT_SIZE,
                                                         SETTING_SERVICE_SERVICE,
                                                         LABEL_ENTITY_DOMAIN, LABEL_ENTITY_ENTITY,
                                                         LABEL_SERVICE_SERVICE,
                                                         LABEL_SETTINGS_ENTITY,
                                                         LABEL_SETTINGS_SERVICE,
                                                         LABEL_ICON_SHOW_ICON,
                                                         LABEL_SETTINGS_ICON,
                                                         SETTING_ICON_SHOW_ICON,
                                                         CONNECT_NOTIFY_SELECTED,
                                                         CONNECT_NOTIFY_ACTIVE,
                                                         SETTING_ENTITY_DOMAIN,
                                                         EMPTY_STRING, ATTRIBUTE_FRIENDLY_NAME,
                                                         LABEL_TEXT_SHOW_TEXT, LABEL_TEXT_SIZE,
                                                         LABEL_TEXT_SHOW_UNIT,
                                                         SETTING_TEXT_SHOW_UNIT,
                                                         LABEL_TEXT_UNIT_LINE_BREAK,
                                                         SETTING_TEXT_UNIT_LINE_BREAK,
                                                         LABEL_TEXT_VALUE, CONNECT_CHANGED,
                                                         ATTRIBUTES,
                                                         SETTING_TEXT_ATTRIBUTE,
                                                         LABEL_TEXT_ADAPTIVE_SIZE,
                                                         SETTING_TEXT_ADAPTIVE_SIZE,
                                                         ATTRIBUTE_UNIT_OF_MEASUREMENT, STATE,
                                                         LABEL_ICON_OPACITY, SETTING_ICON_OPACITY,
                                                         ATTRIBUTE_ICON,
                                                         ICON_COLOR_ON, ICON_COLOR_OFF,
                                                         MDI_SVG_JSON, LABEL_ICON_SCALE,
                                                         SETTING_ICON_SCALE,
                                                         DEFAULT_ICON_SCALE, DEFAULT_ICON_SHOW_ICON,
                                                         DEFAULT_ICON_OPACITY,
                                                         DEFAULT_TEXT_SHOW_TEXT,
                                                         DEFAULT_TEXT_POSITION,
                                                         DEFAULT_TEXT_ADAPTIVE_SIZE,
                                                         DEFAULT_TEXT_SIZE,
                                                         DEFAULT_TEXT_SHOW_UNIT,
                                                         DEFAULT_TEXT_UNIT_LINE_BREAK,
                                                         LABEL_SERVICE_PARAMETERS,
                                                         ATTRIBUTE_FIELDS,
                                                         SETTING_SERVICE_PARAMETERS,
                                                         CONNECT_NOTIFY_TEXT, LABEL_ICON_NO_ENTITY,
                                                         LABEL_ICON_NO_ENTITY_ICON,
                                                         CONNECT_NOTIFY_ENABLE_EXPANSION,
                                                         LABEL_TEXT_NO_ENTITY)

from GtkHelper.GtkHelper import BetterExpander
from locales.LegacyLocaleManager import LegacyLocaleManager

MDI_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", MDI_SVG_JSON)

with open(MDI_FILENAME, "r", encoding="utf-8") as f:
    MDI_ICONS: Dict[str, str] = json.loads(f.read())


class HomeAssistantAction(HomeAssistantActionBase):
    """
    Action to be loaded by StreamController.
    """
    settings: Dict[str, Any]

    uuid: uuid.UUID

    lm: LegacyLocaleManager
    combo_factory: SignalListItemFactory

    entity_domain_combo: ComboRow
    entity_domain_model: StringList

    entity_entity_combo: ComboRow
    entity_entity_model: StringList

    service_service_combo: ComboRow
    service_service_model: StringList

    service_parameters: BetterExpander

    icon_show_icon: SwitchRow
    icon_scale: SpinRow
    icon_opacity: SpinRow

    text_show_text: SwitchRow
    text_attribute_combo: ComboRow
    text_attribute_model: StringList
    text_position_combo: ComboRow
    text_position_model: StringList
    text_adaptive_size: SwitchRow
    text_size: SpinRow
    text_show_unit: SwitchRow
    text_unit_line_break: SwitchRow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.has_configuration = True

        self.uuid = uuid.uuid4()

    def on_ready(self) -> None:
        """
        Set up action when StreamController has finished loading.
        """
        settings = self.get_settings()
        migrated_settings = migration.migrate(settings)
        self.set_settings(migrated_settings)

        self.settings = migrated_settings

        if not self.plugin_base.backend.is_connected():
            self.plugin_base.backend.register_action(self.on_ready)
            return

        entity = self._get_setting(SETTING_ENTITY_ENTITY)

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.uuid, self._entity_updated)

        self._entity_updated(entity)

    def on_remove(self) -> None:
        """
        Clean up after action was removed.
        """
        self.plugin_base.backend.remove_action(self.on_ready)
        self.plugin_base.backend.remove_tracked_entity(self._get_setting(SETTING_ENTITY_ENTITY),
                                                       self.uuid)

        self._entity_updated("")

    def on_key_down(self) -> None:
        """
        Call the service stated in the settings.
        """
        entity = self.settings.get(SETTING_ENTITY_ENTITY)
        service = self.settings.get(SETTING_SERVICE_SERVICE)

        if not entity or not service:
            return

        parameters = {}

        for parameter, value in self.settings.get(SETTING_SERVICE_PARAMETERS, {}).items():
            try:
                # try to create a dict or list from the value
                value = json.loads(value)
            except JSONDecodeError:
                # if it doesn't work just keep it as is
                pass

            parameters[parameter] = value

        self.plugin_base.backend.call_service(entity, service, parameters)

    def get_config_rows(self) -> list:
        """
        Get the rows to be displayed in the UI.
        """
        self.lm = self.plugin_base.locale_manager

        rows: list = super().get_config_rows()

        self.combo_factory = SignalListItemFactory()
        self.combo_factory.connect(CONNECT_BIND, self._factory_bind)

        entity_group = self._get_entity_group()
        service_group = self._get_service_group()
        icon_group = self._get_icon_group()
        text_group = self._get_text_group()

        self._load_domains()

        self._set_enabled_disabled()

        # connect as the last action - else the on_change functions trigger on populating the models
        self._connect_rows()

        if self.plugin_base.backend.is_connected():
            # already connected to home assistant -> put global settings at the bottom
            return [entity_group, service_group, icon_group, text_group, *rows]

        return [*rows, entity_group, service_group, icon_group, text_group]

    def _get_entity_group(self) -> PreferencesGroup:
        """
        Get all entity rows.
        """
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
        """
        Get all service rows.
        """
        self.service_service_combo = ComboRow(title=self.lm.get(LABEL_SERVICE_SERVICE))
        self.service_service_combo.set_factory(self.combo_factory)
        self.service_parameters = BetterExpander(title=self.lm.get(LABEL_SERVICE_PARAMETERS))

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_SERVICE))
        group.set_margin_top(20)
        group.add(self.service_service_combo)
        group.add(self.service_parameters)

        return group

    def _get_icon_group(self) -> PreferencesGroup:
        """
        Get all icon rows.
        """
        self.icon_show_icon = ExpanderRow(title=self.lm.get(LABEL_ICON_SHOW_ICON))
        self.icon_show_icon.set_show_enable_switch(True)
        self.icon_show_icon.set_enable_expansion(
            self._get_setting(SETTING_ICON_SHOW_ICON, DEFAULT_ICON_SHOW_ICON))

        self.icon_scale = SpinRow.new_with_range(1, 100, 1)
        self.icon_scale.set_title(self.lm.get(LABEL_ICON_SCALE))
        self.icon_scale.set_value(self._get_setting(SETTING_ICON_SCALE, DEFAULT_ICON_SCALE))

        self.icon_opacity = SpinRow.new_with_range(1, 100, 1)
        self.icon_opacity.set_title(self.lm.get(LABEL_ICON_OPACITY))
        self.icon_opacity.set_value(self._get_setting(SETTING_ICON_OPACITY, DEFAULT_ICON_OPACITY))

        self.icon_show_icon.add_row(self.icon_scale)
        self.icon_show_icon.add_row(self.icon_opacity)

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_ICON))
        group.set_margin_top(20)
        group.add(self.icon_show_icon)

        return group

    def _get_text_group(self) -> PreferencesGroup:
        """
        Get all text rows.
        """
        self.text_show_text = ExpanderRow(title=self.lm.get(LABEL_TEXT_SHOW_TEXT))
        self.text_show_text.set_show_enable_switch(True)
        self.text_show_text.set_enable_expansion(
            self._get_setting(SETTING_TEXT_SHOW_TEXT, DEFAULT_TEXT_SHOW_TEXT))

        self.text_position_model = StringList.new(
            [TEXT_POSITION_TOP, TEXT_POSITION_CENTER, TEXT_POSITION_BOTTOM])

        self.text_position_combo = ComboRow(title=self.lm.get(LABEL_TEXT_POSITION))
        self.text_position_combo.set_factory(self.combo_factory)
        self.text_position_combo.set_model(self.text_position_model)

        _set_value_in_combo(self.text_position_combo, self.text_position_model,
                            self._get_setting(SETTING_TEXT_POSITION, DEFAULT_TEXT_POSITION))

        self.text_adaptive_size = SwitchRow(title=self.lm.get(LABEL_TEXT_ADAPTIVE_SIZE))
        self.text_adaptive_size.set_active(
            self._get_setting(SETTING_TEXT_ADAPTIVE_SIZE, DEFAULT_TEXT_ADAPTIVE_SIZE))

        self.text_size = SpinRow.new_with_range(0, 100, 1)
        self.text_size.set_title(self.lm.get(LABEL_TEXT_SIZE))
        self.text_size.set_value(self._get_setting(SETTING_TEXT_SIZE, DEFAULT_TEXT_SIZE))

        self.text_show_unit = SwitchRow(title=self.lm.get(LABEL_TEXT_SHOW_UNIT))
        self.text_show_unit.set_active(
            self._get_setting(SETTING_TEXT_SHOW_UNIT, DEFAULT_TEXT_SHOW_UNIT))

        self.text_unit_line_break = SwitchRow(title=self.lm.get(LABEL_TEXT_UNIT_LINE_BREAK))
        self.text_unit_line_break.set_active(
            self._get_setting(SETTING_TEXT_UNIT_LINE_BREAK, DEFAULT_TEXT_UNIT_LINE_BREAK))

        self.text_attribute_combo = ComboRow(title=self.lm.get(LABEL_TEXT_VALUE))
        self.text_attribute_combo.set_factory(self.combo_factory)

        self._load_attributes()

        self.text_show_text.add_row(self.text_attribute_combo)
        self.text_show_text.add_row(self.text_position_combo)
        self.text_show_text.add_row(self.text_adaptive_size)
        self.text_show_text.add_row(self.text_size)
        self.text_show_text.add_row(self.text_show_unit)
        self.text_show_text.add_row(self.text_unit_line_break)

        group = PreferencesGroup()
        group.set_title(self.lm.get(LABEL_SETTINGS_TEXT))
        group.set_margin_top(20)
        group.add(self.text_show_text)

        return group

    def _connect_rows(self) -> None:
        """
        Connect all input fields to functions to be called on changes.
        """
        self.entity_domain_combo.connect(CONNECT_NOTIFY_SELECTED, self._on_change_domain)
        self.entity_entity_combo.connect(CONNECT_NOTIFY_SELECTED, self._on_change_entity)

        self.service_service_combo.connect(CONNECT_NOTIFY_SELECTED, self._on_change_service)

        self.icon_show_icon.connect(CONNECT_NOTIFY_ENABLE_EXPANSION,
                                    self._on_change_expansion_switch,
                                    SETTING_ICON_SHOW_ICON)
        self.icon_scale.connect(CONNECT_CHANGED, self._on_change_spin, SETTING_ICON_SCALE)
        self.icon_opacity.connect(CONNECT_CHANGED, self._on_change_spin, SETTING_ICON_OPACITY)

        self.text_show_text.connect(CONNECT_NOTIFY_ENABLE_EXPANSION,
                                    self._on_change_expansion_switch,
                                    SETTING_TEXT_SHOW_TEXT)
        self.text_position_combo.connect(CONNECT_NOTIFY_SELECTED, self._on_change_combo,
                                         SETTING_TEXT_POSITION)
        self.text_adaptive_size.connect(CONNECT_NOTIFY_ACTIVE, self._on_change_switch,
                                        SETTING_TEXT_ADAPTIVE_SIZE)
        self.text_size.connect(CONNECT_CHANGED, self._on_change_spin, SETTING_TEXT_SIZE)
        self.text_show_unit.connect(CONNECT_NOTIFY_ACTIVE, self._on_change_switch,
                                    SETTING_TEXT_SHOW_UNIT)
        self.text_unit_line_break.connect(CONNECT_NOTIFY_ACTIVE, self._on_change_switch,
                                          SETTING_TEXT_UNIT_LINE_BREAK)
        self.text_attribute_combo.connect(CONNECT_NOTIFY_SELECTED, self._on_change_combo,
                                          SETTING_TEXT_ATTRIBUTE)

    def _on_change_switch(self, switch, *args):
        """
        Execute when a switch is changed.
        """
        self.settings[args[1]] = switch.get_active()
        self.set_settings(self.settings)

        if args[1] == SETTING_ICON_SHOW_ICON:
            self._entity_updated(self.settings.get(SETTING_ENTITY_ENTITY))

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(SETTING_ENTITY_ENTITY))

    def _on_change_expansion_switch(self, expander, *args):
        """
        Execute when the switch of an ExpanderRow is changed.
        """
        self.settings[args[1]] = expander.get_enable_expansion()
        self.set_settings(self.settings)

        if args[1] == SETTING_ICON_SHOW_ICON:
            self._entity_updated(self.settings.get(SETTING_ENTITY_ENTITY))

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(SETTING_ENTITY_ENTITY))

    def _factory_bind(self, _, item):
        """
        Set text and tooltip for combo row entries.
        """
        label = Label(halign=Align.END)
        item.set_child(label)

        text = item.get_item().get_string()

        friendly_name = self.plugin_base.backend.get_entity(text).get(ATTRIBUTES, {}).get(
            ATTRIBUTE_FRIENDLY_NAME,
            EMPTY_STRING)

        label.set_text(text)
        label.set_tooltip_text(friendly_name if friendly_name else text)

    def _on_change_domain(self, combo, _):
        """
        Execute when the domain is changed.
        """
        old_domain = self.settings.setdefault(SETTING_ENTITY_DOMAIN, EMPTY_STRING)

        domain = combo.get_selected_item().get_string()

        if old_domain != domain:
            old_entity = self.settings[SETTING_ENTITY_ENTITY]

            if old_entity:
                self.plugin_base.backend.remove_tracked_entity(old_entity, self.uuid)

            self.settings[SETTING_ENTITY_DOMAIN] = domain
            self.settings[SETTING_ENTITY_ENTITY] = EMPTY_STRING
            self.settings[SETTING_SERVICE_SERVICE] = EMPTY_STRING
            self.set_settings(self.settings)

            self.entity_entity_combo.set_model(None)
            self.service_service_combo.set_model(None)
            self.set_media(image=None)

        if domain:
            self._load_entities()
            self._load_services()

        self._set_enabled_disabled()

    def _on_change_entity(self, combo, _):
        """
        Execute when the entity is changed.
        """
        old_entity = self.settings[SETTING_ENTITY_ENTITY]
        entity = combo.get_selected_item().get_string()

        if old_entity == entity:
            return

        self.settings[SETTING_ENTITY_ENTITY] = entity
        self.set_settings(self.settings)

        if old_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, self.uuid)

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.uuid, self._entity_updated)

            self._load_attributes()
            self._load_service_parameters()

        self._entity_updated(entity)

        self._set_enabled_disabled()

    def _on_change_service(self, combo, _):
        """
        Execute when the service is changed.
        """
        value = combo.get_selected_item().get_string()
        self.settings[SETTING_SERVICE_SERVICE] = value
        self.settings[SETTING_SERVICE_PARAMETERS] = {}

        self.set_settings(self.settings)

        self._load_service_parameters()

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(SETTING_ENTITY_ENTITY))

    def _on_change_parameters_combo(self, combo, *args):
        """
        Execute when a new selection is made in a combo row for a service parameter.
        """
        value = combo.get_selected_item().get_string()
        if value:
            self.settings[SETTING_SERVICE_PARAMETERS][args[1]] = value
        else:
            self.settings[SETTING_SERVICE_PARAMETERS].pop(args[1])
        self.set_settings(self.settings)

    def _on_change_parameters_switch(self, switch, *args):
        """
        Execute when a switch is changed in a combo row for a service parameter.
        """
        self.settings[SETTING_SERVICE_PARAMETERS][args[1]] = switch.get_active()
        self.set_settings(self.settings)

    def _on_change_parameters_entry(self, entry, *args):
        """
        Execute when the text is changed in an entry row for a service parameter.
        """
        value = entry.get_text()
        if value:
            self.settings[SETTING_SERVICE_PARAMETERS][args[1]] = value
        else:
            self.settings[SETTING_SERVICE_PARAMETERS].pop(args[1])
        self.set_settings(self.settings)

    def _on_change_combo(self, combo, *args):
        """
        Execute when a new selection is made in a combo row.
        """
        value = combo.get_selected_item().get_string()
        self.settings[args[1]] = value
        self.set_settings(self.settings)

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(SETTING_ENTITY_ENTITY))

    def _on_change_spin(self, spin, *args):
        """
        Execute when the number is changed in a spin row.
        """
        size = spin.get_value()
        self.settings[args[0]] = size
        self.set_settings(self.settings)

        self._entity_updated(self.settings.get(SETTING_ENTITY_ENTITY))

    def _entity_updated(self, entity: str, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        show_icon = self.settings.get(SETTING_ICON_SHOW_ICON)
        show_text = self.settings.get(SETTING_TEXT_SHOW_TEXT)

        if not entity or (not show_icon and not show_text):
            self.set_media(image=None)
            self.set_top_label(None)
            self.set_center_label(None)
            self.set_bottom_label(None)
            return

        settings_entity = self.settings.get(SETTING_ENTITY_ENTITY)

        if entity != settings_entity:
            logging.error("Mismatching entities; settings: %s, callback: %s", settings_entity,
                          entity)
            return

        if show_icon or show_text and state is None:
            state = self.plugin_base.backend.get_entity(entity)

        self._update_icon(show_icon, state)

        if show_text:
            self._update_labels(show_text, state)
        else:
            self.set_top_label(None)
            self.set_center_label(None)
            self.set_bottom_label(None)

        self._set_enabled_disabled()

    def _update_icon(self, show_icon: bool, state: dict):
        """
        Update the icon to reflect the entity state.
        """
        if not show_icon or not state:
            self.set_media(image=None)
            return

        icon = self._get_icon(state)

        if icon:
            png_data = cairosvg.svg2png(bytestring=icon, dpi=600)

            image = Image.open(io.BytesIO(png_data))

            scale = round(self.settings.get(SETTING_ICON_SCALE, DEFAULT_ICON_SCALE) / 100, 2)

            self.set_media(image=image, size=scale)
        else:
            self.set_media(image=None)

    def _update_labels(self, show_text: bool, state: dict):
        """
        Update the labels to reflect the entity state.
        """
        if not show_text or not state:
            self.set_top_label(None)
            self.set_center_label(None)
            self.set_bottom_label(None)
            return

        text = str(state.get(STATE))
        text_length = len(text)
        text_height = 1
        attribute = self.settings.get(SETTING_TEXT_ATTRIBUTE)

        if attribute == STATE:
            if self.settings.get(SETTING_TEXT_SHOW_UNIT):
                unit = state.get(ATTRIBUTES, {}).get(ATTRIBUTE_UNIT_OF_MEASUREMENT,
                                                     EMPTY_STRING)

                if self.settings.get(SETTING_TEXT_UNIT_LINE_BREAK):
                    text_length = max(len(text), len(unit))
                    text = f"{text}\n{unit}"
                    text_height = 2
                else:
                    text = f"{text} {unit}"
                    text_length = len(text)
        else:
            text = str(state.get(ATTRIBUTES, {}).get(attribute, EMPTY_STRING))
            text_length = len(text)

        position = self.settings.get(SETTING_TEXT_POSITION)
        font_size = self.settings.get(SETTING_TEXT_SIZE)

        if self.settings.get(SETTING_TEXT_ADAPTIVE_SIZE):
            if text_length == 1:
                font_size = 50
            elif text_length == 2:
                font_size = 40
            else:
                font_size = 30 - 3 * (text_length - 3)

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

    def _load_domains(self):
        """
        Load domains from Home Assistant.
        """
        old_domain = self.settings.get(SETTING_ENTITY_DOMAIN, EMPTY_STRING)

        self.entity_domain_model = StringList.new([EMPTY_STRING])
        self.entity_domain_combo.set_model(self.entity_domain_model)

        domains = sorted(self.plugin_base.backend.get_domains())

        for domain in domains:
            self.entity_domain_model.append(domain)

        if old_domain in domains:
            _set_value_in_combo(self.entity_domain_combo, self.entity_domain_model, old_domain)
            self._load_entities()
            self._load_services()

    def _load_entities(self):
        """
        Load entities from Home Assistant.
        """
        old_entity = self.settings.get(SETTING_ENTITY_ENTITY, EMPTY_STRING)

        self.entity_entity_model = StringList.new([EMPTY_STRING])
        self.entity_entity_combo.set_model(self.entity_entity_model)

        entities = sorted(
            self.plugin_base.backend.get_entities(
                self.entity_domain_combo.get_selected_item().get_string()))

        for entity in entities:
            self.entity_entity_model.append(entity)

        _set_value_in_combo(self.entity_entity_combo, self.entity_entity_model, old_entity)

    def _load_services(self):
        """
        Load services from Home Assistant.
        """
        old_service = self.settings.get(SETTING_SERVICE_SERVICE, EMPTY_STRING)

        self.service_service_model = StringList.new([EMPTY_STRING])
        self.service_service_combo.set_model(self.service_service_model)

        services = self.plugin_base.backend.get_services(
            self.entity_domain_combo.get_selected_item().get_string())

        for service in services.keys():
            self.service_service_model.append(service)

        _set_value_in_combo(self.service_service_combo, self.service_service_model, old_service)
        self._load_service_parameters()

    def _load_service_parameters(self):
        """
        Load service parameters from Home Assistant.
        """
        ha_entity = self.plugin_base.backend.get_entity(self.settings[SETTING_ENTITY_ENTITY])
        # supported_parameters = ha_entity.get(ATTRIBUTES, {}).keys()

        self.service_parameters.clear()

        service = self.settings[SETTING_SERVICE_SERVICE]

        fields = self.plugin_base.backend.get_services(
            self.entity_domain_combo.get_selected_item().get_string()).get(
            service, {}).get(ATTRIBUTE_FIELDS, {})

        fields.update(fields.get("advanced_fields", {}).get(ATTRIBUTE_FIELDS, {}))
        fields.pop("advanced_fields", None)

        for field in fields:
            # if field not in supported_parameters:
            #     continue

            setting_value = self.settings.get(SETTING_SERVICE_PARAMETERS, {}).get(field)

            selector = list(fields[field]["selector"].keys())[0]

            if selector == "select" or f"{field}_list" in ha_entity.get(ATTRIBUTES, {}).keys():
                if selector == "select":
                    options = fields[field]["selector"]["select"]["options"]
                else:
                    options = ha_entity.get(ATTRIBUTES, {})[f"{field}_list"]

                if not isinstance(options[0], str):
                    options = [opt["value"] for opt in options]

                model = StringList.new([EMPTY_STRING, *options])

                row = ComboRow(title=field)
                row.set_model(model)
                row.connect(CONNECT_NOTIFY_SELECTED, self._on_change_parameters_combo, field)

                if setting_value:
                    _set_value_in_combo(row, model, setting_value)
            elif selector == "boolean":
                row = SwitchRow(title=field)
                row.connect(CONNECT_NOTIFY_ACTIVE, self._on_change_parameters_switch, field)

                if setting_value:
                    row.set_active(bool(setting_value))
                else:
                    default_value = fields[field].get("default")
                    if default_value:
                        row.set_active(bool(default_value))
            # elif selector == "number":
            #     number_min = fields[field]["selector"]["number"]["min"]
            #     number_max = fields[field]["selector"]["number"]["max"]
            #     number_step = fields[field]["selector"]["number"].get("step", 1)
            #
            #     row = SpinRow.new_with_range(number_min, number_max, number_step)
            #     row.set_title(field)
            #     row.connect(CONNECT_CHANGED, self.on_change_parameters_spin, field)
            else:
                row = EntryRow(title=field)
                row.connect(CONNECT_NOTIFY_TEXT, self._on_change_parameters_entry, field)

                if setting_value:
                    row.set_text(str(setting_value))

            self.service_parameters.add_row(row)

    def _load_attributes(self):
        """
        Load entity attributes from Home Assistant.
        """
        old_attribute = self.settings.get(SETTING_TEXT_ATTRIBUTE, EMPTY_STRING)

        ha_entity = self.plugin_base.backend.get_entity(self._get_setting(SETTING_ENTITY_ENTITY))

        self.text_attribute_model = StringList.new([STATE])

        for attribute in ha_entity.get(ATTRIBUTES, {}).keys():
            self.text_attribute_model.append(attribute)

        self.text_attribute_combo.set_model(self.text_attribute_model)

        _set_value_in_combo(self.text_attribute_combo, self.text_attribute_model, old_attribute)

    def _get_setting(self, setting: str, default: Any = None) -> Any:
        """
        Get one setting from the settings with an optional default.
        """
        value = self.settings.setdefault(setting, default)
        self.set_settings(self.settings)
        return value

    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        if not hasattr(self, "entity_domain_combo") or self.entity_domain_combo is None:
            # check any attribute to see if rows are initialized and need to be updated
            return

        # Entity section
        domain = self.entity_domain_combo.get_selected_item().get_string() if (
            self.entity_domain_combo.get_selected_item()) else False
        domain_selected = bool(domain)
        self.entity_entity_combo.set_sensitive(
            domain_selected and len(self.entity_entity_model) > 1)
        self.service_service_combo.set_sensitive(
            domain_selected and len(self.service_service_model) > 1)

        # Service section
        if len(self.service_parameters.get_rows()) > 0:
            self.service_parameters.set_sensitive(True)
        else:
            self.service_parameters.set_sensitive(False)
            self.service_parameters.set_expanded(False)

        entity = self.entity_entity_combo.get_selected_item().get_string() if (
            self.entity_entity_combo.get_selected_item()) else False
        is_entity_set = bool(entity)

        # Icon section
        ha_entity = self.plugin_base.backend.get_entity(
            self._get_setting(SETTING_ENTITY_ENTITY))
        ha_entity_icon = ha_entity.get(ATTRIBUTES, {}).get(ATTRIBUTE_ICON, None)
        has_icon = bool(ha_entity_icon)

        if not is_entity_set:
            self.icon_show_icon.set_sensitive(False)
            self.icon_show_icon.set_enable_expansion(False)
            self.icon_show_icon.set_subtitle(self.lm.get(LABEL_ICON_NO_ENTITY))
        elif not has_icon:
            self.icon_show_icon.set_sensitive(False)
            self.icon_show_icon.set_enable_expansion(False)
            self.icon_show_icon.set_subtitle(self.lm.get(LABEL_ICON_NO_ENTITY_ICON))
        else:
            self.icon_show_icon.set_sensitive(True)
            self.icon_show_icon.set_subtitle(EMPTY_STRING)

        # Text section
        if not is_entity_set:
            self.text_show_text.set_sensitive(False)
            self.text_show_text.set_enable_expansion(False)
            self.text_show_text.set_subtitle(self.lm.get(LABEL_TEXT_NO_ENTITY))
        else:
            self.text_show_text.set_sensitive(True)
            self.text_show_text.set_subtitle(EMPTY_STRING)

            ha_entity = self.plugin_base.backend.get_entity(
                self._get_setting(SETTING_ENTITY_ENTITY))

            self.text_attribute_combo.set_sensitive(len(self.text_attribute_model) > 1)
            self.text_position_combo.set_sensitive(True)
            self.text_adaptive_size.set_sensitive(True)
            self.text_size.set_sensitive(not self.text_adaptive_size.get_active())

            has_unit = bool(ha_entity.get(ATTRIBUTES, {}).get(ATTRIBUTE_UNIT_OF_MEASUREMENT, False))

            attribute = self.text_attribute_combo.get_selected_item().get_string() if (
                self.text_attribute_combo.get_selected_item()) else False
            no_attribute_selected = not bool(attribute)

            unit_rows_active = has_unit and no_attribute_selected

            if unit_rows_active:
                self.text_show_unit.set_sensitive(True)
                self.text_unit_line_break.set_sensitive(True)
            else:
                self.text_show_unit.set_active(False)
                self.text_show_unit.set_sensitive(False)
                self.text_unit_line_break.set_active(False)
                self.text_unit_line_break.set_sensitive(False)

            if not self.text_show_unit.get_active():
                self.text_unit_line_break.set_active(False)
                self.text_unit_line_break.set_sensitive(False)

    def _get_icon(self, state: dict) -> str:
        """
        Get the item corresponding to the given state.
        """
        domain = self.settings.get(SETTING_ENTITY_DOMAIN)

        if "media_player" == domain:
            service = self.settings.get(SETTING_SERVICE_SERVICE)
            # use icons for service instead of entity
            if "media_play_pause" == service:
                if "playing" == state.get(STATE):
                    icon_name = "pause"
                else:
                    icon_name = "play"
            elif "media_stop" == service:
                icon_name = "stop"
            elif "volume_up" == service:
                icon_name = "volume-plus"
            elif "volume_down" == service:
                icon_name = "volume-minus"
            elif "media_next_track" == service:
                icon_name = "skip-next"
            elif "media_previous_track" == service:
                icon_name = "skip-previous"
            else:
                logging.warning("Icon not found for domain %s and service %s", domain, service)
                icon_name = "alert-circle"

            color = ICON_COLOR_ON
        else:
            icon_name = state.get(ATTRIBUTES, {}).get(ATTRIBUTE_ICON, EMPTY_STRING)

            color = ICON_COLOR_ON if "on" == state.get(STATE) else ICON_COLOR_OFF

        icon_path = self._get_icon_path(icon_name)

        opacity = str(round(self.settings.get(SETTING_ICON_OPACITY, DEFAULT_ICON_OPACITY) / 100, 2))

        icon = _get_icon_svg(icon_name, icon_path)

        return (
            icon
            .replace("<color>", color)
            .replace("<opacity>", opacity)
        )

    def _get_icon_path(self, name: str) -> str:
        """
        Get the SVG path for the icon's MDI name.
        """
        if "mdi:" in name:
            name = name.replace("mdi:", EMPTY_STRING)

        return MDI_ICONS.get(name, EMPTY_STRING)


def _get_icon_svg(name: str, path: str) -> str:
    """
    Build a complete SVG string from an icons' name and path.
    """
    if not path:
        return EMPTY_STRING

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 24 '
            f'24"><title>{name}</title><path d="{path}" fill="<color>" opacity="<opacity>" '
            f'/></svg>')


def _set_value_in_combo(combo: ComboRow, model: StringList, value: str):
    """
    Select the entry in the combo row corresponding to the index of the model equalling the given
    value. Does nothing if the value does not exist in the model.
    """
    if not value:
        return

    for i in range(len(model)):
        if model.get_string(i) == value:
            combo.set_selected(i)
            return
