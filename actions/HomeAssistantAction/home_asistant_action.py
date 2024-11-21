"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import io
import json
import logging
import uuid
from json import JSONDecodeError
from typing import Any, Dict, List

import cairosvg
import gi
from PIL import Image

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import Align, Button, Label, PropertyExpression, \
    SignalListItemFactory, StringList, StringObject
from gi.repository.Adw import ActionRow, ComboRow, EntryRow, \
    ExpanderRow, PreferencesGroup, SpinRow, SwitchRow

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import migration, icon_helper, \
    text_helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization_window import \
    CustomizationWindow
from de_gensyn_HomeAssistantPlugin.home_assistant_action_base import HomeAssistantActionBase
from de_gensyn_HomeAssistantPlugin import const

from GtkHelper.GtkHelper import BetterExpander
from locales.LegacyLocaleManager import LegacyLocaleManager


class HomeAssistantAction(HomeAssistantActionBase):
    """
    Action to be loaded by StreamController.
    """
    settings: Dict[str, Any]

    uuid: uuid.UUID

    lm: LegacyLocaleManager
    combo_factory: SignalListItemFactory
    combo_expression: PropertyExpression = PropertyExpression.new(StringObject, None, "string")

    entity_domain_combo: ComboRow
    entity_domain_model: StringList

    entity_entity_combo: ComboRow
    entity_entity_model: StringList

    service_call_service: ExpanderRow
    service_service_combo: ComboRow
    service_service_model: StringList

    service_parameters: BetterExpander

    icon_show_icon: ExpanderRow
    icon_scale: SpinRow
    icon_opacity: SpinRow
    icon_custom_icons_expander: BetterExpander
    icon_custom_icons: List = []
    icon_custom_icon_add: Button

    text_show_text: ExpanderRow
    text_attribute_combo: ComboRow
    text_round: ExpanderRow
    text_round_precision: SpinRow
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
        settings = migration.migrate(self.get_settings())
        self.set_settings(settings)

        self.settings = settings

        if not self.plugin_base.backend.is_connected():
            self.plugin_base.backend.register_action(self.on_ready)
            return

        entity = self.settings.get(const.SETTING_ENTITY_ENTITY)

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.uuid, self._entity_updated)

        self._entity_updated(entity)

    def on_remove(self) -> None:
        """
        Clean up after action was removed.
        """
        self.plugin_base.backend.remove_action(self.on_ready)
        self.plugin_base.backend.remove_tracked_entity(
            self.settings.get(const.SETTING_ENTITY_ENTITY),
            self.uuid)

        self._entity_updated("")

    def on_key_down(self) -> None:
        """
        Call the service stated in the settings.
        """
        entity = self.settings.get(const.SETTING_ENTITY_ENTITY)
        service = self.settings.get(const.SETTING_SERVICE_SERVICE)

        if not entity or not service:
            return

        parameters = {}

        for parameter, value in self.settings.get(const.SETTING_SERVICE_PARAMETERS, {}).items():
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
        self.combo_factory.connect(const.CONNECT_BIND, self._factory_bind)

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
        self.entity_domain_combo = ComboRow(title=self.lm.get(const.LABEL_ENTITY_DOMAIN))
        self.entity_domain_combo.set_enable_search(True)
        self.entity_domain_combo.set_expression(self.combo_expression)

        self.entity_entity_combo = ComboRow(title=self.lm.get(const.LABEL_ENTITY_ENTITY))
        self.entity_entity_combo.set_factory(self.combo_factory)
        self.entity_entity_combo.set_enable_search(True)
        self.entity_entity_combo.set_expression(self.combo_expression)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_ENTITY))
        group.set_margin_top(20)
        group.add(self.entity_domain_combo)
        group.add(self.entity_entity_combo)

        return group

    def _get_service_group(self) -> PreferencesGroup:
        """
        Get all service rows.
        """
        self.service_call_service = ExpanderRow(title=self.lm.get(const.LABEL_SERVICE_CALL_SERVICE))
        self.service_call_service.set_show_enable_switch(True)
        self.service_call_service.set_enable_expansion(
            self.settings.get(const.SETTING_SERVICE_CALL_SERVICE,
                              const.DEFAULT_SERVICE_CALL_SERVICE))

        self.service_service_combo = ComboRow(title=self.lm.get(const.LABEL_SERVICE_SERVICE))
        self.service_service_combo.set_factory(self.combo_factory)
        self.service_service_combo.set_enable_search(True)
        self.service_service_combo.set_expression(self.combo_expression)

        self.service_parameters = BetterExpander(title=self.lm.get(const.LABEL_SERVICE_PARAMETERS))

        self.service_call_service.add_row(self.service_service_combo)
        self.service_call_service.add_row(self.service_parameters)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_SERVICE))
        group.set_margin_top(20)
        group.add(self.service_call_service)

        return group

    def _get_icon_group(self) -> PreferencesGroup:
        """
        Get all icon rows.
        """
        self.icon_show_icon = ExpanderRow(title=self.lm.get(const.LABEL_ICON_SHOW_ICON))
        self.icon_show_icon.set_show_enable_switch(True)
        self.icon_show_icon.set_enable_expansion(
            self.settings.get(const.SETTING_ICON_SHOW_ICON, const.DEFAULT_ICON_SHOW_ICON))

        self.icon_scale = SpinRow.new_with_range(1, 100, 1)
        self.icon_scale.set_title(self.lm.get(const.LABEL_ICON_SCALE))
        self.icon_scale.set_value(
            self.settings.get(const.SETTING_ICON_SCALE, const.DEFAULT_ICON_SCALE))

        self.icon_opacity = SpinRow.new_with_range(1, 100, 1)
        self.icon_opacity.set_title(self.lm.get(const.LABEL_ICON_OPACITY))
        self.icon_opacity.set_value(
            self.settings.get(const.SETTING_ICON_OPACITY, const.DEFAULT_ICON_OPACITY))

        self.icon_custom_icon_add = Button(icon_name="list-add", valign=Align.CENTER)
        self.icon_custom_icon_add.set_size_request(15, 15)

        self.icon_custom_icons_expander = BetterExpander(
            title=self.lm.get(const.LABEL_ICON_CUSTOM_ICONS))
        self.icon_custom_icons_expander.add_suffix(self.icon_custom_icon_add)

        self._load_custom_icons()

        self.icon_show_icon.add_row(self.icon_scale)
        self.icon_show_icon.add_row(self.icon_opacity)
        self.icon_show_icon.add_row(self.icon_custom_icons_expander)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_ICON))
        group.set_margin_top(20)
        group.add(self.icon_show_icon)

        return group

    def _on_add_custom_icon(self, _, index: int = None):
        attributes = []

        for i in range(self.text_attribute_model.get_n_items()):
            attributes.append(self.text_attribute_model.get_item(i).get_string())

        if index is not None and index > -1:
            current = self.icon_custom_icons[index]
        else:
            current = None

        window = CustomizationWindow(CustomizationWindow.Customization.ICON, self.lm, attributes,
                                     self._add_custom_icon,
                                     icons=list(icon_helper.MDI_ICONS.keys()),
                                     current=current, index=index)
        window.show()

    def _add_custom_icon(self, attribute: str, operator: str, value: str, target: str, index: int):
        custom_icon = {
            "attribute": attribute,
            "operator": operator,
            "value": value,
            "icon": target
        }

        if custom_icon in self.icon_custom_icons:
            if index is not None and index > -1:
                # edited item is identical to existing - delete it
                self.icon_custom_icons.pop(index)
                self._load_custom_icons()

            # no duplicates necessary
            return

        if index is not None and index > -1:
            self.icon_custom_icons[index] = custom_icon
        else:
            self.icon_custom_icons.append(custom_icon)

        self.settings[const.SETTING_CUSTOMIZATION_ICONS] = self.icon_custom_icons
        self.set_settings(self.settings)
        self._load_custom_icons()
        self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

    def _get_text_group(self) -> PreferencesGroup:
        """
        Get all text rows.
        """
        self.text_show_text = ExpanderRow(title=self.lm.get(const.LABEL_TEXT_SHOW_TEXT))
        self.text_show_text.set_show_enable_switch(True)
        self.text_show_text.set_enable_expansion(
            self.settings.get(const.SETTING_TEXT_SHOW_TEXT, const.DEFAULT_TEXT_SHOW_TEXT))

        self.text_attribute_combo = ComboRow(title=self.lm.get(const.LABEL_TEXT_VALUE))
        self.text_attribute_combo.set_factory(self.combo_factory)

        self.text_round = ExpanderRow(title=self.lm.get(const.LABEL_TEXT_ROUND))
        self.text_round.set_show_enable_switch(True)
        self.text_round.set_enable_expansion(
            self.settings.get(const.SETTING_TEXT_ROUND, const.DEFAULT_TEXT_ROUND))

        self.text_round_precision = SpinRow.new_with_range(0, 20, 1)
        self.text_round_precision.set_title(self.lm.get(const.LABEL_TEXT_ROUND_PRECISION))
        self.text_round_precision.set_value(
            self.settings.get(const.SETTING_TEXT_ROUND_PRECISION,
                              const.DEFAULT_TEXT_ROUND_PRECISION))

        self.text_round.add_row(self.text_round_precision)

        self.text_position_model = StringList.new(
            [const.TEXT_POSITION_TOP, const.TEXT_POSITION_CENTER, const.TEXT_POSITION_BOTTOM])

        self.text_position_combo = ComboRow(title=self.lm.get(const.LABEL_TEXT_POSITION))
        self.text_position_combo.set_factory(self.combo_factory)
        self.text_position_combo.set_model(self.text_position_model)

        _set_value_in_combo(self.text_position_combo, self.text_position_model,
                            self.settings.get(const.SETTING_TEXT_POSITION,
                                              const.DEFAULT_TEXT_POSITION))

        self.text_adaptive_size = SwitchRow(title=self.lm.get(const.LABEL_TEXT_ADAPTIVE_SIZE))
        self.text_adaptive_size.set_active(
            self.settings.get(const.SETTING_TEXT_ADAPTIVE_SIZE, const.DEFAULT_TEXT_ADAPTIVE_SIZE))

        self.text_size = SpinRow.new_with_range(0, 100, 1)
        self.text_size.set_title(self.lm.get(const.LABEL_TEXT_SIZE))
        self.text_size.set_value(
            self.settings.get(const.SETTING_TEXT_SIZE, const.DEFAULT_TEXT_SIZE))

        self.text_show_unit = SwitchRow(title=self.lm.get(const.LABEL_TEXT_SHOW_UNIT))
        self.text_show_unit.set_active(
            self.settings.get(const.SETTING_TEXT_SHOW_UNIT, const.DEFAULT_TEXT_SHOW_UNIT))

        self.text_unit_line_break = SwitchRow(title=self.lm.get(const.LABEL_TEXT_UNIT_LINE_BREAK))
        self.text_unit_line_break.set_active(
            self.settings.get(const.SETTING_TEXT_UNIT_LINE_BREAK,
                              const.DEFAULT_TEXT_UNIT_LINE_BREAK))

        self._load_attributes()

        self.text_show_text.add_row(self.text_attribute_combo)
        self.text_show_text.add_row(self.text_round)
        self.text_show_text.add_row(self.text_position_combo)
        self.text_show_text.add_row(self.text_adaptive_size)
        self.text_show_text.add_row(self.text_size)
        self.text_show_text.add_row(self.text_show_unit)
        self.text_show_text.add_row(self.text_unit_line_break)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_TEXT))
        group.set_margin_top(20)
        group.add(self.text_show_text)

        return group

    def _connect_rows(self) -> None:
        """
        Connect all input fields to functions to be called on changes.
        """
        self.entity_domain_combo.connect(const.CONNECT_NOTIFY_SELECTED, self._on_change_domain)
        self.entity_entity_combo.connect(const.CONNECT_NOTIFY_SELECTED, self._on_change_entity)

        self.service_call_service.connect(const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                                          self._on_change_expansion_switch,
                                          const.SETTING_SERVICE_CALL_SERVICE)
        self.service_service_combo.connect(const.CONNECT_NOTIFY_SELECTED, self._on_change_service)

        self.icon_show_icon.connect(const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                                    self._on_change_expansion_switch,
                                    const.SETTING_ICON_SHOW_ICON)
        self.icon_scale.connect(const.CONNECT_CHANGED, self._on_change_spin,
                                const.SETTING_ICON_SCALE)
        self.icon_opacity.connect(const.CONNECT_CHANGED, self._on_change_spin,
                                  const.SETTING_ICON_OPACITY)
        self.icon_custom_icon_add.connect(const.CONNECT_CLICKED, self._on_add_custom_icon)

        self.text_show_text.connect(const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                                    self._on_change_expansion_switch,
                                    const.SETTING_TEXT_SHOW_TEXT)
        self.text_attribute_combo.connect(const.CONNECT_NOTIFY_SELECTED, self._on_change_combo,
                                          const.SETTING_TEXT_ATTRIBUTE)
        self.text_round.connect(const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                                self._on_change_expansion_switch,
                                const.SETTING_TEXT_ROUND)
        self.text_round_precision.connect(const.CONNECT_CHANGED, self._on_change_spin,
                                          const.SETTING_TEXT_ROUND_PRECISION)
        self.text_position_combo.connect(const.CONNECT_NOTIFY_SELECTED, self._on_change_combo,
                                         const.SETTING_TEXT_POSITION)
        self.text_adaptive_size.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_switch,
                                        const.SETTING_TEXT_ADAPTIVE_SIZE)
        self.text_size.connect(const.CONNECT_CHANGED, self._on_change_spin, const.SETTING_TEXT_SIZE)
        self.text_show_unit.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_switch,
                                    const.SETTING_TEXT_SHOW_UNIT)
        self.text_unit_line_break.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_switch,
                                          const.SETTING_TEXT_UNIT_LINE_BREAK)

    def _on_change_switch(self, switch, *args):
        """
        Execute when a switch is changed.
        """
        self.settings[args[1]] = switch.get_active()
        self.set_settings(self.settings)

        if args[1] == const.SETTING_ICON_SHOW_ICON:
            self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

    def _on_change_expansion_switch(self, expander, *args):
        """
        Execute when the switch of an ExpanderRow is changed.
        """
        self.settings[args[1]] = expander.get_enable_expansion()
        self.set_settings(self.settings)

        if args[1] == const.SETTING_ICON_SHOW_ICON:
            self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

    def _factory_bind(self, _, item):
        """
        Set text and tooltip for combo row entries.
        """
        label = Label(halign=Align.END)
        item.set_child(label)

        text = item.get_item().get_string()

        friendly_name = self.plugin_base.backend.get_entity(text).get(const.ATTRIBUTES, {}).get(
            const.ATTRIBUTE_FRIENDLY_NAME,
            const.EMPTY_STRING)

        label.set_text(text)
        label.set_tooltip_text(friendly_name if friendly_name else text)

    def _on_change_domain(self, combo, _):
        """
        Execute when the domain is changed.
        """
        old_domain = self.settings.setdefault(const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING)

        domain = combo.get_selected_item().get_string()

        if old_domain != domain:
            old_entity = self.settings.get(const.SETTING_ENTITY_ENTITY)

            if old_entity:
                self.plugin_base.backend.remove_tracked_entity(old_entity, self.uuid)

            self.settings[const.SETTING_ENTITY_DOMAIN] = domain
            self.settings[const.SETTING_ENTITY_ENTITY] = const.EMPTY_STRING
            self.settings[const.SETTING_SERVICE_CALL_SERVICE] = const.DEFAULT_SERVICE_CALL_SERVICE
            self.settings[const.SETTING_SERVICE_SERVICE] = const.EMPTY_STRING
            self.settings[const.SETTING_ICON_SHOW_ICON] = const.DEFAULT_ICON_SHOW_ICON
            self.settings[const.SETTING_TEXT_SHOW_TEXT] = const.DEFAULT_TEXT_SHOW_TEXT
            self.icon_custom_icons.clear()
            self.settings.get(const.SETTING_CUSTOMIZATION_ICONS, []).clear()
            self._load_custom_icons()
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
        old_entity = self.settings[const.SETTING_ENTITY_ENTITY]
        entity = combo.get_selected_item().get_string()

        if old_entity == entity:
            return

        self.settings[const.SETTING_ENTITY_ENTITY] = entity
        self.icon_custom_icons.clear()
        self.settings.get(const.SETTING_CUSTOMIZATION_ICONS, []).clear()
        self._load_custom_icons()
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
        value = combo.get_selected_item().get_string() if combo.get_selected_item() else ""
        self.settings[const.SETTING_SERVICE_SERVICE] = value
        self.settings[const.SETTING_SERVICE_PARAMETERS] = {}

        self.set_settings(self.settings)

        self._load_service_parameters()

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

    def _on_change_parameters_combo(self, combo, *args):
        """
        Execute when a new selection is made in a combo row for a service parameter.
        """
        value = combo.get_selected_item().get_string()
        if value:
            self.settings[const.SETTING_SERVICE_PARAMETERS][args[1]] = value
        else:
            self.settings[const.SETTING_SERVICE_PARAMETERS].pop(args[1])
        self.set_settings(self.settings)

    def _on_change_parameters_switch(self, switch, *args):
        """
        Execute when a switch is changed in a combo row for a service parameter.
        """
        self.settings[const.SETTING_SERVICE_PARAMETERS][args[1]] = switch.get_active()
        self.set_settings(self.settings)

    def _on_change_parameters_entry(self, entry, *args):
        """
        Execute when the text is changed in an entry row for a service parameter.
        """
        value = entry.get_text()
        if value:
            self.settings[const.SETTING_SERVICE_PARAMETERS][args[1]] = value
        else:
            self.settings[const.SETTING_SERVICE_PARAMETERS].pop(args[1])
        self.set_settings(self.settings)

    def _on_change_combo(self, combo, *args):
        """
        Execute when a new selection is made in a combo row.
        """
        value = combo.get_selected_item().get_string()
        self.settings[args[1]] = value
        self.set_settings(self.settings)

        self._set_enabled_disabled()

        self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

    def _on_change_spin(self, spin, *args):
        """
        Execute when the number is changed in a spin row.
        """
        size = spin.get_value()
        self.settings[args[0]] = size
        self.set_settings(self.settings)

        self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

    def _entity_updated(self, entity: str, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        show_icon = self.settings.get(const.SETTING_ICON_SHOW_ICON)
        show_text = self.settings.get(const.SETTING_TEXT_SHOW_TEXT)

        if not entity or (not show_icon and not show_text):
            self.set_media(image=None)
            self.set_top_label(const.EMPTY_STRING)
            self.set_center_label(const.EMPTY_STRING)
            self.set_bottom_label(const.EMPTY_STRING)
            return

        settings_entity = self.settings.get(const.SETTING_ENTITY_ENTITY)

        if entity != settings_entity:
            logging.error("Mismatching entities; settings: %s, callback: %s", settings_entity,
                          entity)
            return

        if show_icon or show_text and state is None:
            state = self.plugin_base.backend.get_entity(entity)

        self._update_icon(show_icon, state)
        self._update_labels(show_text, state)
        self._set_enabled_disabled()

    def _update_icon(self, show_icon: bool, state: dict):
        """
        Update the icon to reflect the entity state.
        """
        if not show_icon or not state:
            self.set_media(image=None)
            return

        icon = icon_helper.get_icon(state, self.settings)

        if icon:
            png_data = cairosvg.svg2png(bytestring=icon, dpi=600)
            image = Image.open(io.BytesIO(png_data))
            scale = round(
                self.settings.get(const.SETTING_ICON_SCALE, const.DEFAULT_ICON_SCALE) / 100, 2)
            self.set_media(image=image, size=scale)
        else:
            self.set_media(image=None)

    def _update_labels(self, show_text: bool, state: dict):
        """
        Update the labels to reflect the entity state.
        """
        if not show_text or not state:
            self.set_top_label(const.EMPTY_STRING)
            self.set_center_label(const.EMPTY_STRING)
            self.set_bottom_label(const.EMPTY_STRING)
            return

        text, position, font_size = text_helper.get_text(state, self.settings)

        if position == const.TEXT_POSITION_TOP:
            self.set_top_label(text, font_size=font_size)
            self.set_center_label(const.EMPTY_STRING)
            self.set_bottom_label(const.EMPTY_STRING)
        elif position == const.TEXT_POSITION_BOTTOM:
            self.set_top_label(const.EMPTY_STRING)
            self.set_center_label(const.EMPTY_STRING)
            self.set_bottom_label(text, font_size=font_size)
        else:
            self.set_top_label(const.EMPTY_STRING)
            self.set_center_label(text, font_size=font_size)
            self.set_bottom_label(const.EMPTY_STRING)

    def _load_domains(self):
        """
        Load domains from Home Assistant.
        """
        old_domain = self.settings.get(const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING)

        self.entity_domain_model = StringList.new([const.EMPTY_STRING])
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
        old_entity = self.settings.get(const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING)

        self.entity_entity_model = StringList.new([const.EMPTY_STRING])
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
        old_service = self.settings.get(const.SETTING_SERVICE_SERVICE, const.EMPTY_STRING)

        self.service_service_model = StringList.new([])
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
        ha_entity = self.plugin_base.backend.get_entity(self.settings[const.SETTING_ENTITY_ENTITY])
        # supported_parameters = ha_entity.get(ATTRIBUTES, {}).keys()

        self.service_parameters.clear()

        service = self.settings[const.SETTING_SERVICE_SERVICE]

        fields = self.plugin_base.backend.get_services(
            self.entity_domain_combo.get_selected_item().get_string()).get(
            service, {}).get(const.ATTRIBUTE_FIELDS, {})

        fields.update(fields.get("advanced_fields", {}).get(const.ATTRIBUTE_FIELDS, {}))
        fields.pop("advanced_fields", None)

        for field in fields:
            # if field not in supported_parameters:
            #     continue

            setting_value = self.settings.get(const.SETTING_SERVICE_PARAMETERS, {}).get(field)

            selector = list(fields[field]["selector"].keys())[0]

            if selector == "select" or f"{field}_list" in ha_entity.get(const.ATTRIBUTES,
                                                                        {}).keys():
                if selector == "select":
                    options = fields[field]["selector"]["select"]["options"]
                else:
                    options = ha_entity.get(const.ATTRIBUTES, {})[f"{field}_list"]

                if not isinstance(options[0], str):
                    options = [opt["value"] for opt in options]

                model = StringList.new([const.EMPTY_STRING, *options])

                row = ComboRow(title=field)
                row.set_model(model)
                row.connect(const.CONNECT_NOTIFY_SELECTED, self._on_change_parameters_combo, field)

                if setting_value:
                    _set_value_in_combo(row, model, setting_value)
            elif selector == "boolean":
                row = SwitchRow(title=field)
                row.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_parameters_switch, field)

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
                row.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_parameters_entry, field)

                if setting_value:
                    row.set_text(str(setting_value))

            self.service_parameters.add_row(row)

    def _load_attributes(self):
        """
        Load entity attributes from Home Assistant.
        """
        old_attribute = self.settings.get(const.SETTING_TEXT_ATTRIBUTE, const.EMPTY_STRING)

        ha_entity = self.plugin_base.backend.get_entity(
            self.settings.get(const.SETTING_ENTITY_ENTITY))

        self.text_attribute_model = StringList.new([const.STATE])

        for attribute in ha_entity.get(const.ATTRIBUTES, {}).keys():
            self.text_attribute_model.append(attribute)

        self.text_attribute_combo.set_model(self.text_attribute_model)

        _set_value_in_combo(self.text_attribute_combo, self.text_attribute_model, old_attribute)

    def _load_custom_icons(self):
        self.icon_custom_icons_expander.clear()

        self.icon_custom_icons = self.settings.get(const.SETTING_CUSTOMIZATION_ICONS, [])

        for index, custom_icon in enumerate(self.icon_custom_icons):
            edit_button = Button(icon_name="edit", valign=Align.CENTER)
            edit_button.set_size_request(15, 15)
            edit_button.connect(const.CONNECT_CLICKED, self._on_edit_custom_icon, index)

            delete_button = Button(icon_name="user-trash", valign=Align.CENTER)
            delete_button.set_size_request(15, 15)
            delete_button.connect(const.CONNECT_CLICKED, self._on_delete_custom_icon, index)

            row = ActionRow(
                title=f"{self.lm.get(const.LABEL_CUSTOMIZATION_IF)} "
                      f"{self.lm.get(const.LABEL_CUSTOMIZATION_ATTRIBUTE).lower()} "
                      f"\"{custom_icon['attribute']}\" "
                      f"{self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS[custom_icon['operator']])} "
                      f"\"{custom_icon['value']}\" "
                      f"{self.lm.get(const.LABEL_CUSTOMIZATION_THEN)} "
                      f"\"{custom_icon['icon']}\".")
            row.add_suffix(edit_button)
            row.add_suffix(delete_button)

            self.icon_custom_icons_expander.add_row(row)

    def _on_edit_custom_icon(self, _, index: int):
        self._on_add_custom_icon(_, index)

    def _on_delete_custom_icon(self, _, index: int):
        self.icon_custom_icons.pop(index)

        # the settings have been implicitly changed by altering the custom icon list
        self.set_settings(self.settings)

        self._load_custom_icons()
        self._entity_updated(self.settings.get(const.SETTING_ENTITY_ENTITY))

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
        is_domain_set = bool(domain)
        self.entity_entity_combo.set_sensitive(
            is_domain_set and self.entity_entity_model.get_n_items() > 1)

        # Service section
        entity = self.settings.get(const.SETTING_ENTITY_ENTITY)
        is_entity_set = bool(entity)

        if not is_domain_set:
            self.service_call_service.set_sensitive(False)
            self.service_call_service.set_enable_expansion(False)
            self.service_call_service.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_DOMAIN))
        elif not is_entity_set:
            self.service_call_service.set_sensitive(False)
            self.service_call_service.set_enable_expansion(False)
            self.service_call_service.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_ENTITY))
        elif self.service_service_model.get_n_items() == 0:
            self.service_call_service.set_sensitive(False)
            self.service_call_service.set_enable_expansion(False)
            self.service_call_service.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_SERVICES))
        else:
            self.service_call_service.set_sensitive(True)
            self.service_call_service.set_subtitle(const.EMPTY_STRING)

        if len(self.service_parameters.get_rows()) > 0:
            self.service_parameters.set_sensitive(True)
            self.service_parameters.set_subtitle(const.EMPTY_STRING)
        else:
            self.service_parameters.set_sensitive(False)
            self.service_parameters.set_expanded(False)
            self.service_parameters.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_PARAMETERS))

        # Icon section
        if not is_entity_set:
            self.icon_show_icon.set_sensitive(False)
            self.icon_show_icon.set_enable_expansion(False)
            self.icon_show_icon.set_subtitle(self.lm.get(const.LABEL_ICON_NO_ENTITY))
        else:
            self.icon_show_icon.set_sensitive(True)
            self.icon_show_icon.set_subtitle(const.EMPTY_STRING)

        # Text section
        if not is_entity_set:
            self.text_show_text.set_sensitive(False)
            self.text_show_text.set_enable_expansion(False)
            self.text_show_text.set_subtitle(self.lm.get(const.LABEL_TEXT_NO_ENTITY))
        else:
            self.text_show_text.set_sensitive(True)
            self.text_show_text.set_subtitle(const.EMPTY_STRING)

            ha_entity = self.plugin_base.backend.get_entity(
                self.settings.get(const.SETTING_ENTITY_ENTITY))

            self.text_attribute_combo.set_sensitive(self.text_attribute_model.get_n_items() > 1)
            self.text_position_combo.set_sensitive(True)
            self.text_adaptive_size.set_sensitive(True)
            self.text_size.set_sensitive(not self.text_adaptive_size.get_active())

            has_unit = bool(
                ha_entity.get(const.ATTRIBUTES, {}).get(const.ATTRIBUTE_UNIT_OF_MEASUREMENT, False))

            if has_unit:
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


def _set_value_in_combo(combo: ComboRow, model: StringList, value: str):
    """
    Select the entry in the combo row corresponding to the index of the model equalling the given
    value. Does nothing if the value does not exist in the model.
    """
    if not value:
        return

    for i in range(model.get_n_items()):
        if model.get_string(i) == value:
            combo.set_selected(i)
            return
