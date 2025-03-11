"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import io
import json
import uuid
from functools import partial
from json import JSONDecodeError
from typing import Any, Dict, List

import cairosvg
import gi
from PIL import Image

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.scale_row import ScaleRow
from src.backend.PluginManager.ActionBase import ActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import Align, Button, Label, PropertyExpression, \
    SignalListItemFactory, StringList, StringObject, Box, Orientation, ColorButton
from gi.repository.Adw import ActionRow, ComboRow, EntryRow, \
    ExpanderRow, PreferencesGroup, SpinRow, SwitchRow
from gi.repository import GLib
from gi.repository.Gdk import RGBA

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import icon_helper, \
    text_helper, settings_helper, service_parameters_helper, helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization_window import \
    CustomizationWindow
from de_gensyn_HomeAssistantPlugin import const

from GtkHelper.GtkHelper import BetterExpander
from locales.LegacyLocaleManager import LegacyLocaleManager


class HomeAssistantAction(ActionBase):
    """
    Action to be loaded by StreamController.
    """
    initialized: bool = False

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
    icon_custom_icons_expander: BetterExpander

    text_show_text: ExpanderRow
    text_attribute_combo: ComboRow
    text_round_precision: SpinRow
    text_text_color: ColorButton
    text_outline_color: ColorButton
    text_attribute_model: StringList
    text_position_combo: ComboRow
    text_show_unit: SwitchRow
    text_unit_line_break: SwitchRow

    connection_status: ActionRow

    connect_rows: List = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.has_configuration = True

        self.uuid = uuid.uuid4()

    def on_ready(self) -> None:
        """
        Set up action when StreamController has finished loading.
        """
        settings = settings_helper.migrate(self.get_settings())
        settings = settings_helper.fill_defaults(settings)
        self.set_settings(settings)

        self.settings = settings

        if not self.plugin_base.backend.is_connected():
            self.plugin_base.backend.register_action(self.on_ready)

        entity = self.settings[const.SETTING_ENTITY_ENTITY]

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.uuid, self._entity_updated)

        self._entity_updated()

    def on_remove(self) -> None:
        """
        Clean up after action was removed.
        """
        self.plugin_base.backend.remove_action(self.on_ready)
        self.plugin_base.backend.remove_tracked_entity(
            self.settings[const.SETTING_ENTITY_ENTITY],
            self.uuid)

        self._entity_updated()

    def on_key_down(self) -> None:
        """
        Call the service stated in the settings.
        """
        entity = self.settings[const.SETTING_ENTITY_ENTITY]
        service = self.settings[const.SETTING_SERVICE_SERVICE]

        if not entity or not service:
            return

        parameters = {}

        for parameter, value in self.settings[const.SETTING_SERVICE_PARAMETERS].items():
            try:
                # try to create a dict or list from the value
                value = json.loads(value)
            except (JSONDecodeError, TypeError):
                # if it doesn't work just keep it as is
                pass

            parameters[parameter] = value

        self.plugin_base.backend.call_service(entity, service, parameters)

    def get_config_rows(self) -> list:
        """
        Get the rows to be displayed in the UI.
        """
        self.lm = self.plugin_base.locale_manager

        self.combo_factory = SignalListItemFactory()
        self.connect_rows.append(
            partial(self.combo_factory.connect, const.CONNECT_BIND, self._factory_bind))

        entity_group = self._get_entity_group()
        service_group = self._get_service_group()
        icon_group = self._get_icon_group()
        text_group = self._get_text_group()
        connection_group = self._get_connection_group()

        self.initialized = True

        self._load_domains()

        self._set_enabled_disabled()

        # connect as the last action - else the on_change functions trigger on populating the models
        self._connect_rows()

        return [entity_group, service_group, icon_group, text_group, connection_group]

    def _get_entity_group(self) -> PreferencesGroup:
        """
        Get all entity rows.
        """
        self.entity_domain_combo = ComboRow(title=self.lm.get(const.LABEL_ENTITY_DOMAIN))
        self.entity_domain_combo.set_enable_search(True)
        self.entity_domain_combo.set_expression(self.combo_expression)
        self.connect_rows.append(
            partial(self.entity_domain_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_domain))

        self.entity_entity_combo = ComboRow(title=self.lm.get(const.LABEL_ENTITY_ENTITY))
        self.entity_entity_combo.set_factory(self.combo_factory)
        self.entity_entity_combo.set_enable_search(True)
        self.entity_entity_combo.set_expression(self.combo_expression)
        self.connect_rows.append(
            partial(self.entity_entity_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_entity))

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
            self.settings[const.SETTING_SERVICE_CALL_SERVICE])
        self.connect_rows.append(
            partial(self.service_call_service.connect, const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                    self._on_change_expansion_switch,
                    const.SETTING_SERVICE_CALL_SERVICE))

        self.service_service_combo = ComboRow(title=self.lm.get(const.LABEL_SERVICE_SERVICE))
        self.service_service_combo.set_factory(self.combo_factory)
        self.service_service_combo.set_enable_search(True)
        self.service_service_combo.set_expression(self.combo_expression)
        self.connect_rows.append(
            partial(self.service_service_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_service))

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

        """
        Icon show icon
        """
        self.icon_show_icon = ExpanderRow(title=self.lm.get(const.LABEL_ICON_SHOW_ICON))
        self.icon_show_icon.set_show_enable_switch(True)
        self.icon_show_icon.set_enable_expansion(self.settings[const.SETTING_ICON_SHOW_ICON])
        self.connect_rows.append(
            partial(self.icon_show_icon.connect, const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                    self._on_change_expansion_switch,
                    const.SETTING_ICON_SHOW_ICON))

        """
        Icon icon
        """
        icon_icon = EntryRow(title=self.lm.get(const.LABEL_ICON_ICON))
        icon_icon.set_text(self.settings[const.SETTING_ICON_ICON])
        self.connect_rows.append(
            partial(icon_icon.connect, const.CONNECT_NOTIFY_TEXT, self._on_change_entry,
                    const.SETTING_ICON_ICON))

        """
        Icon icon color
        """
        icon_color = ColorButton()
        rgba_list = self.settings[const.SETTING_ICON_COLOR]
        rgba = RGBA()
        rgba.red = rgba_list[0]
        rgba.green = rgba_list[1]
        rgba.blue = rgba_list[2]
        rgba.alpha = 1
        icon_color.set_rgba(rgba)
        self.connect_rows.append(
            partial(icon_color.connect, const.CONNECT_NOTIFY_COLOR_SET, self._on_change_color,
                    const.SETTING_ICON_COLOR))

        icon_color_row = ActionRow(title=self.lm.get(const.LABEL_ICON_COLOR))
        icon_color_row.add_suffix(icon_color)

        """
        Icon scale
        """
        icon_scale_row: ScaleRow = ScaleRow(self.lm.get(const.LABEL_ICON_SCALE),
                                            self.settings[const.SETTING_ICON_SCALE],
                                            0, 100, 1)
        self.connect_rows.append(
            partial(icon_scale_row.connect, const.CONNECT_VALUE_CHANGED, self._on_change_scale,
                    const.SETTING_ICON_SCALE))

        """
        Icon opacity
        """
        icon_opacity_row: ScaleRow = ScaleRow(self.lm.get(const.LABEL_ICON_OPACITY),
                                              self.settings[const.SETTING_ICON_OPACITY],
                                              0, 100, 1)
        self.connect_rows.append(
            partial(icon_opacity_row.connect, const.CONNECT_VALUE_CHANGED, self._on_change_scale,
                    const.SETTING_ICON_OPACITY))


        """
        Icon custom icon
        """
        icon_custom_icon_add = Button(icon_name="list-add", valign=Align.CENTER)
        icon_custom_icon_add.set_size_request(15, 15)
        self.connect_rows.append(
            partial(icon_custom_icon_add.connect, const.CONNECT_CLICKED, self._on_add_custom_icon))

        self.icon_custom_icons_expander = BetterExpander(
            title=self.lm.get(const.LABEL_ICON_CUSTOM_ICONS))
        self.icon_custom_icons_expander.add_suffix(icon_custom_icon_add)

        self._load_custom_icons()

        self.icon_show_icon.add_row(icon_icon)
        self.icon_show_icon.add_row(icon_color_row)
        self.icon_show_icon.add_row(icon_scale_row)
        self.icon_show_icon.add_row(icon_opacity_row)
        self.icon_show_icon.add_row(self.icon_custom_icons_expander)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_ICON))
        group.set_margin_top(20)
        group.add(self.icon_show_icon)

        return group

    def _get_connection_group(self) -> PreferencesGroup:
        """
        Get all connection rows.
        """

        """
        Connection status
        """
        self.connection_status = ActionRow(title=self.lm.get(const.SETTING_CONNECTION_STATUS))
        self.connection_status.set_title(
            const.CONNECTED if self.plugin_base.backend.is_connected() else const.NOT_CONNECTED)

        self.plugin_base.backend.set_connection_status_callback(self.set_connection_status)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_CONNECTION))
        group.set_margin_top(20)
        group.add(self.connection_status)

        return group

    def _on_add_custom_icon(self, _, index: int = -1):
        attributes = []

        for i in range(self.text_attribute_model.get_n_items()):
            attributes.append(self.text_attribute_model.get_item(i).get_string())

        if index > -1:
            current = self.settings[const.SETTING_CUSTOMIZATION_ICONS][index]
        else:
            current = None

        window = CustomizationWindow(CustomizationWindow.Customization.ICON, self.lm, attributes,
                                     self._add_custom_icon,
                                     icons=list(icon_helper.MDI_ICONS),
                                     current=current, index=index)
        window.show()

    def _add_custom_icon(self, attribute: str, operator: str, value: str, icon: str, color: str,
                         scale: int, opacity: int, index: int):
        custom_icon = {
            const.CUSTOM_ATTRIBUTE: attribute,
            const.CUSTOM_OPERATOR: operator,
            const.CUSTOM_VALUE: value
        }

        if icon:
            custom_icon[const.CUSTOM_ICON_ICON] = icon

        if color:
            custom_icon[const.CUSTOM_ICON_COLOR] = color

        if scale:
            custom_icon[const.CUSTOM_ICON_SCALE] = scale

        if opacity:
            custom_icon[const.CUSTOM_ICON_OPACITY] = opacity

        custom_icons_to_check_for_duplicates = self.settings[
            const.SETTING_CUSTOMIZATION_ICONS].copy()

        if index > -1:
            # we have to check for duplicates without the item being edited because it may have
            # not been changed
            custom_icons_to_check_for_duplicates.pop(index)

        if custom_icon in custom_icons_to_check_for_duplicates:
            if index > -1:
                # edited item is identical to existing - delete it
                self.settings[const.SETTING_CUSTOMIZATION_ICONS].pop(index)
                self.set_settings(self.settings)

            self._load_custom_icons()
            self._entity_updated()
            return

        if index > -1:
            self.settings[const.SETTING_CUSTOMIZATION_ICONS][index] = custom_icon
        else:
            self.settings[const.SETTING_CUSTOMIZATION_ICONS].append(custom_icon)

        self.set_settings(self.settings)
        self._load_custom_icons()
        self._entity_updated()

    def _get_text_group(self) -> PreferencesGroup:
        """
        Get all text rows.
        """

        """
        Text show text
        """
        self.text_show_text = ExpanderRow(title=self.lm.get(const.LABEL_TEXT_SHOW_TEXT))
        self.text_show_text.set_show_enable_switch(True)
        self.text_show_text.set_enable_expansion(self.settings[const.SETTING_TEXT_SHOW_TEXT])
        self.connect_rows.append(
            partial(self.text_show_text.connect, const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                    self._on_change_expansion_switch,
                    const.SETTING_TEXT_SHOW_TEXT))

        """
        Text attribute
        """
        self.text_attribute_combo = ComboRow(title=self.lm.get(const.LABEL_TEXT_ATTRIBUTE))
        self.text_attribute_combo.set_factory(self.combo_factory)
        self.connect_rows.append(
            partial(self.text_attribute_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_combo,
                    const.SETTING_TEXT_ATTRIBUTE))

        """
        Text round
        """
        text_round = ExpanderRow(title=self.lm.get(const.LABEL_TEXT_ROUND))
        text_round.set_show_enable_switch(True)
        text_round.set_enable_expansion(self.settings[const.SETTING_TEXT_ROUND])
        self.connect_rows.append(partial(text_round.connect, const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                                         self._on_change_expansion_switch,
                                         const.SETTING_TEXT_ROUND))

        """
        Text round precision
        """
        text_round_precision = SpinRow.new_with_range(0, 20, 1)
        text_round_precision.set_title(self.lm.get(const.LABEL_TEXT_ROUND_PRECISION))
        text_round_precision.set_value(self.settings[const.SETTING_TEXT_ROUND_PRECISION])
        self.connect_rows.append(
            partial(text_round_precision.connect, const.CONNECT_CHANGED, self._on_change_spin,
                    const.SETTING_TEXT_ROUND_PRECISION))

        text_round.add_row(text_round_precision)

        """
        Text color
        """
        text_rgba_list = self.settings[const.SETTING_TEXT_TEXT_COLOR]
        text_rgba = RGBA()
        text_rgba.red = text_rgba_list[0]
        text_rgba.green = text_rgba_list[1]
        text_rgba.blue = text_rgba_list[2]
        text_rgba.alpha = 1

        text_text_color = ColorButton()
        text_text_color.set_rgba(text_rgba)
        self.connect_rows.append(
            partial(text_text_color.connect, const.CONNECT_NOTIFY_COLOR_SET, self._on_change_color,
                    const.SETTING_TEXT_TEXT_COLOR))

        text_color_row = ActionRow(title=self.lm.get(const.LABEL_TEXT_TEXT_COLOR))
        text_color_row.add_suffix(text_text_color)

        """
        Text outline color
        """
        self.text_outline_color = ColorButton()
        outline_rgba_list = self.settings[const.SETTING_TEXT_OUTLINE_COLOR]
        outline_rgba = RGBA()
        outline_rgba.red = outline_rgba_list[0]
        outline_rgba.green = outline_rgba_list[1]
        outline_rgba.blue = outline_rgba_list[2]
        outline_rgba.alpha = 1
        self.text_outline_color.set_rgba(outline_rgba)
        self.connect_rows.append(
            partial(self.text_outline_color.connect, const.CONNECT_NOTIFY_COLOR_SET,
                    self._on_change_color,
                    const.SETTING_TEXT_OUTLINE_COLOR))

        outline_color_row = ActionRow(title=self.lm.get(const.LABEL_TEXT_OUTLINE_COLOR))
        outline_color_row.add_suffix(self.text_outline_color)

        """
        Text position
        """
        text_position_model = StringList.new(
            [const.TEXT_POSITION_TOP, const.TEXT_POSITION_CENTER, const.TEXT_POSITION_BOTTOM])

        self.text_position_combo = ComboRow(title=self.lm.get(const.LABEL_TEXT_POSITION))
        self.text_position_combo.set_factory(self.combo_factory)
        self.text_position_combo.set_model(text_position_model)
        self.connect_rows.append(
            partial(self.text_position_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_combo,
                    const.SETTING_TEXT_POSITION))

        helper.set_value_in_combo(self.text_position_combo, text_position_model,
                                  self.settings[const.SETTING_TEXT_POSITION])

        """
        Text size
        """
        text_size = ScaleRow(self.lm.get(const.LABEL_TEXT_SIZE),
                             self.settings[const.SETTING_TEXT_SIZE], 0, 100, 1)
        self.connect_rows.append(
            partial(text_size.connect, const.CONNECT_VALUE_CHANGED, self._on_change_scale,
                    const.SETTING_TEXT_SIZE))

        """
        Text show unit
        """
        self.text_show_unit = SwitchRow(title=self.lm.get(const.LABEL_TEXT_SHOW_UNIT))
        self.text_show_unit.set_active(self.settings[const.SETTING_TEXT_SHOW_UNIT])
        self.connect_rows.append(partial(self.text_show_unit.connect, const.CONNECT_NOTIFY_ACTIVE,
                                         self._on_change_switch,
                                         const.SETTING_TEXT_SHOW_UNIT))

        """
        Text unit line break
        """
        self.text_unit_line_break = SwitchRow(title=self.lm.get(const.LABEL_TEXT_UNIT_LINE_BREAK))
        self.text_unit_line_break.set_active(
            self.settings[const.SETTING_TEXT_UNIT_LINE_BREAK])
        self.connect_rows.append(
            partial(self.text_unit_line_break.connect, const.CONNECT_NOTIFY_ACTIVE,
                    self._on_change_switch,
                    const.SETTING_TEXT_UNIT_LINE_BREAK))

        self._load_attributes()

        self.text_show_text.add_row(self.text_attribute_combo)
        self.text_show_text.add_row(text_round)
        self.text_show_text.add_row(text_color_row)
        self.text_show_text.add_row(outline_color_row)
        self.text_show_text.add_row(self.text_position_combo)
        self.text_show_text.add_row(text_size)
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
        for connect in self.connect_rows:
            connect()

    def _on_change_entry(self, entry, *args):
        """
        Execute when an entry is changed.
        """
        self.set_setting(args[1], entry.get_text())

        self._set_enabled_disabled()

        self._entity_updated()

    def _on_change_switch(self, switch, *args):
        """
        Execute when a switch is changed.
        """
        self.set_setting(args[1], switch.get_active())

        self._set_enabled_disabled()

        self._entity_updated()

    def _on_change_expansion_switch(self, expander, *args):
        """
        Execute when the switch of an ExpanderRow is changed.
        """
        self.set_setting(args[1], expander.get_enable_expansion())

        self._set_enabled_disabled()

        self._entity_updated()

    def _on_change_color(self, button, *args):
        """
        Execute when a color is changed.
        """
        color = button.get_rgba()
        color_list = [color.red, color.green, color.blue]
        self.set_setting(args[0], color_list)

        self._set_enabled_disabled()

        self._entity_updated()

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
            old_entity = self.settings[const.SETTING_ENTITY_ENTITY]

            if old_entity:
                self.plugin_base.backend.remove_tracked_entity(old_entity, self.uuid)

            self.settings[const.SETTING_ENTITY_DOMAIN] = domain
            self.settings[const.SETTING_ENTITY_ENTITY] = const.EMPTY_STRING
            self.settings[const.SETTING_SERVICE_CALL_SERVICE] = const.DEFAULT_SERVICE_CALL_SERVICE
            self.settings[const.SETTING_SERVICE_SERVICE] = const.EMPTY_STRING
            self.settings[const.SETTING_ICON_SHOW_ICON] = const.DEFAULT_ICON_SHOW_ICON
            self.settings[const.SETTING_TEXT_SHOW_TEXT] = const.DEFAULT_TEXT_SHOW_TEXT
            self.settings[const.SETTING_CUSTOMIZATION_ICONS].clear()

            self.set_settings(self.settings)

            self._load_custom_icons()

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
        self.settings[const.SETTING_CUSTOMIZATION_ICONS].clear()
        self._load_custom_icons()
        self.set_settings(self.settings)

        if old_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, self.uuid)

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.uuid, self._entity_updated)

            self._load_attributes()
            service_parameters_helper.load_service_parameters(self)

        self._entity_updated()

        self._set_enabled_disabled()

    def _on_change_service(self, combo, _):
        """
        Execute when the service is changed.
        """
        value = combo.get_selected_item().get_string() if combo.get_selected_item() else ""
        self.settings[const.SETTING_SERVICE_SERVICE] = value
        self.settings[const.SETTING_SERVICE_PARAMETERS] = {}

        self.set_settings(self.settings)

        service_parameters_helper.load_service_parameters(self)

        self._set_enabled_disabled()

        self._entity_updated()

    def _on_change_combo(self, combo, *args):
        """
        Execute when a new selection is made in a combo row.
        """
        value = combo.get_selected_item().get_string()
        self.settings[args[1]] = value
        self.set_settings(self.settings)

        self._set_enabled_disabled()

        self._entity_updated()

    def _on_change_spin(self, spin, *args):
        """
        Execute when the number is changed in a spin row.
        """
        size = spin.get_value()
        self.settings[args[0]] = size
        self.set_settings(self.settings)

        self._entity_updated()

    def _on_change_scale(self, scale, *args):
        """
        Execute when the value is changed in a scale.
        """
        size = scale.get_value()
        self.settings[args[1]] = size
        self.set_settings(self.settings)

        self._entity_updated()

    def _on_change_spin_event_controller(self, _, *args):
        """
        Execute when the number is changed in a spin row.
        """
        size = args[0].get_value()
        self.settings[args[1]] = size
        self.set_settings(self.settings)

        self._entity_updated()

    def _entity_updated(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        show_icon = self.settings[const.SETTING_ICON_SHOW_ICON]
        show_text = self.settings[const.SETTING_TEXT_SHOW_TEXT]

        if not show_icon and not show_text:
            self.set_media(image=None)
            self.set_top_label(const.EMPTY_STRING)
            self.set_center_label(const.EMPTY_STRING)
            self.set_bottom_label(const.EMPTY_STRING)
            return

        entity = self.settings[const.SETTING_ENTITY_ENTITY]

        if (show_icon or show_text) and state is None:
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

        icon, scale = icon_helper.get_icon(state, self.settings)

        if icon:
            png_data = cairosvg.svg2png(bytestring=icon, dpi=600)
            image = Image.open(io.BytesIO(png_data))
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

        text, text_color, outline_color, position, font_size = text_helper.get_text(state,
                                                                                    self.settings)

        if position == const.TEXT_POSITION_TOP:
            self.set_top_label(text, color=text_color, outline_color=outline_color,
                               font_size=font_size)
            self.set_center_label(const.EMPTY_STRING)
            self.set_bottom_label(const.EMPTY_STRING)
        elif position == const.TEXT_POSITION_BOTTOM:
            self.set_top_label(const.EMPTY_STRING)
            self.set_center_label(const.EMPTY_STRING)
            self.set_bottom_label(text, color=text_color, outline_color=outline_color,
                                  font_size=font_size)
        else:
            self.set_top_label(const.EMPTY_STRING)
            self.set_center_label(text, color=text_color, outline_color=outline_color,
                                  font_size=font_size)
            self.set_bottom_label(const.EMPTY_STRING)

    def _load_domains(self):
        """
        Load domains from Home Assistant.
        """
        old_domain = self.settings[const.SETTING_ENTITY_DOMAIN]

        self.entity_domain_model = StringList.new([const.EMPTY_STRING])
        self.entity_domain_combo.set_model(self.entity_domain_model)

        domains = sorted(self.plugin_base.backend.get_domains())

        if not old_domain in domains:
            domains.append(old_domain)

        for domain in domains:
            self.entity_domain_model.append(domain)

        helper.set_value_in_combo(self.entity_domain_combo, self.entity_domain_model, old_domain)
        self._load_entities()
        self._load_services()

    def _load_entities(self):
        """
        Load entities from Home Assistant.
        """
        old_entity = self.settings[const.SETTING_ENTITY_ENTITY]

        self.entity_entity_model = StringList.new([const.EMPTY_STRING])
        self.entity_entity_combo.set_model(self.entity_entity_model)

        entities = sorted(
            self.plugin_base.backend.get_entities(
                self.entity_domain_combo.get_selected_item().get_string()))

        if not old_entity in entities:
            entities.append(old_entity)

        for entity in entities:
            self.entity_entity_model.append(entity)

        helper.set_value_in_combo(self.entity_entity_combo, self.entity_entity_model, old_entity)

    def _load_services(self):
        """
        Load services from Home Assistant.
        """
        old_service = self.settings[const.SETTING_SERVICE_SERVICE]

        self.service_service_model = StringList.new([])
        self.service_service_combo.set_model(self.service_service_model)

        services = self.plugin_base.backend.get_services(
            self.entity_domain_combo.get_selected_item().get_string())

        for service in services:
            self.service_service_model.append(service)

        helper.set_value_in_combo(self.service_service_combo, self.service_service_model,
                                  old_service)
        service_parameters_helper.load_service_parameters(self)

    def _load_attributes(self):
        """
        Load entity attributes from Home Assistant.
        """
        old_attribute = self.settings[const.SETTING_TEXT_ATTRIBUTE]

        ha_entity = self.plugin_base.backend.get_entity(self.settings[const.SETTING_ENTITY_ENTITY])

        self.text_attribute_model = StringList.new([const.STATE])

        for attribute in ha_entity.get(const.ATTRIBUTES, {}):
            self.text_attribute_model.append(attribute)

        self.text_attribute_combo.set_model(self.text_attribute_model)

        helper.set_value_in_combo(self.text_attribute_combo, self.text_attribute_model,
                                  old_attribute)

    def _load_custom_icons(self):
        self.icon_custom_icons_expander.clear()

        for index, custom_icon in enumerate(self.settings[const.SETTING_CUSTOMIZATION_ICONS]):
            edit_button = Button(icon_name="edit", valign=Align.CENTER)
            edit_button.set_size_request(15, 15)
            edit_button.connect(const.CONNECT_CLICKED, self._on_edit_custom_icon, index)

            delete_button = Button(icon_name="user-trash", valign=Align.CENTER)
            delete_button.set_size_request(15, 15)
            delete_button.connect(const.CONNECT_CLICKED, self._on_delete_custom_icon, index)

            box_operations = Box(orientation=Orientation.VERTICAL, spacing=1)
            box_operations.append(edit_button)
            box_operations.append(delete_button)

            up_button = Button(icon_name="go-up", valign=Align.CENTER)
            up_button.set_size_request(15, 7)
            up_button.connect(const.CONNECT_CLICKED, self._on_move_up, index)
            up_button.set_sensitive(index != 0)

            down_button = Button(icon_name="go-down", valign=Align.CENTER)
            down_button.set_size_request(15, 7)
            down_button.connect(const.CONNECT_CLICKED, self._on_move_down, index)
            down_button.set_sensitive(
                index != len(self.settings[const.SETTING_CUSTOMIZATION_ICONS]) - 1)

            box_arrows = Box(orientation=Orientation.VERTICAL, spacing=1)
            box_arrows.append(up_button)
            box_arrows.append(down_button)

            title = (f"{self.lm.get(const.LABEL_CUSTOMIZATION_IF)} "
                     f"{self.lm.get(const.LABEL_CUSTOMIZATION_ATTRIBUTE).lower()} "
                     f"\"{custom_icon[const.CUSTOM_ATTRIBUTE]}\" "
                     f"{self.lm.get(const.LABEL_CUSTOMIZATION_OPERATORS[custom_icon[const.CUSTOM_OPERATOR]])} "
                     f"\"{custom_icon[const.CUSTOM_VALUE]}\":\n")

            if custom_icon.get(const.CUSTOM_ICON_ICON):
                title += (f"\n{self.lm.get(const.LABEL_ICON_ICON)} "
                          f"{custom_icon[const.CUSTOM_ICON_ICON]}")

            if custom_icon.get(const.CUSTOM_ICON_COLOR):
                color = custom_icon[const.CUSTOM_ICON_COLOR]
                color = (f'#{int(round(color[0] * 255, 0)):02X}'
                         f'{int(round(color[1] * 255, 0)):02X}'
                         f'{int(round(color[2] * 255, 0)):02X}')
                title += (f"\n{self.lm.get(const.LABEL_ICON_COLOR)} "
                          f"{color}")

            if custom_icon.get(const.CUSTOM_ICON_SCALE):
                title += (f"\n{self.lm.get(const.LABEL_ICON_SCALE)} "
                          f"{int(custom_icon[const.CUSTOM_ICON_SCALE])}")

            if custom_icon.get(const.CUSTOM_ICON_OPACITY):
                title += (f"\n{self.lm.get(const.LABEL_ICON_OPACITY)} "
                          f"{int(custom_icon[const.CUSTOM_ICON_OPACITY])}")

            row = ActionRow(
                title=title)
            row.add_suffix(box_operations)
            row.add_suffix(box_arrows)

            self.icon_custom_icons_expander.add_row(row)

    def _on_edit_custom_icon(self, _, index: int):
        self._on_add_custom_icon(_, index)

    def _on_delete_custom_icon(self, _, index: int):
        self.settings[const.SETTING_CUSTOMIZATION_ICONS].pop(index)
        self.set_settings(self.settings)
        self._load_custom_icons()
        self._entity_updated()

    def _on_move_up(self, _, index: int):
        self.settings[const.SETTING_CUSTOMIZATION_ICONS][index], \
            self.settings[const.SETTING_CUSTOMIZATION_ICONS][index - 1] = \
            self.settings[const.SETTING_CUSTOMIZATION_ICONS][index - 1], \
                self.settings[const.SETTING_CUSTOMIZATION_ICONS][index]
        self.set_settings(self.settings)
        self._load_custom_icons()
        self._entity_updated()

    def _on_move_down(self, _, index: int):
        self.settings[const.SETTING_CUSTOMIZATION_ICONS][index], \
            self.settings[const.SETTING_CUSTOMIZATION_ICONS][index + 1] = \
            self.settings[const.SETTING_CUSTOMIZATION_ICONS][index + 1], \
                self.settings[const.SETTING_CUSTOMIZATION_ICONS][index]
        self.set_settings(self.settings)
        self._load_custom_icons()
        self._entity_updated()

    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        if not self.initialized:
            return

        # Entity section
        domain = self.entity_domain_combo.get_selected_item().get_string() if (
            self.entity_domain_combo.get_selected_item()) else False
        is_domain_set = bool(domain)
        self.entity_entity_combo.set_sensitive(
            is_domain_set and self.entity_entity_model.get_n_items() > 1)

        # Service section
        entity = self.settings[const.SETTING_ENTITY_ENTITY]
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
            self.icon_custom_icons_expander.set_expanded(
                len(self.settings[const.SETTING_CUSTOMIZATION_ICONS]) > 0)

        # Text section
        if not is_entity_set:
            self.text_show_text.set_sensitive(False)
            self.text_show_text.set_enable_expansion(False)
            self.text_show_text.set_subtitle(self.lm.get(const.LABEL_TEXT_NO_ENTITY))
        else:
            self.text_show_text.set_sensitive(True)
            self.text_show_text.set_subtitle(const.EMPTY_STRING)

            ha_entity = self.plugin_base.backend.get_entity(
                self.settings[const.SETTING_ENTITY_ENTITY])

            self.text_attribute_combo.set_sensitive(self.text_attribute_model.get_n_items() > 1)
            self.text_position_combo.set_sensitive(True)

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

    def set_connection_status(self, status) -> None:
        """
        Callback function to be executed when the Home Assistant connection status changes.
        """
        GLib.idle_add(self.connection_status.set_title, status)

    def set_setting(self, key, value) -> None:
        """
        Sets the setting in the local copy and also writes it to the disk.
        """
        self.settings[key] = value
        self.set_settings(self.settings)
