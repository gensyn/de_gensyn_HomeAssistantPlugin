"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import json
import uuid
import threading
from functools import partial
from json import JSONDecodeError
from typing import Any, Dict, List

import gi

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_icon_row import CustomizationIconRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.window.customization_icon_window import CustomizationIconWindow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_text_row import CustomizationTextRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.window.customization_text_window import CustomizationTextWindow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper.scale_row import ScaleRow
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.InputIdentifier import Input, InputEvent

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import Align, Button, Label, PropertyExpression, \
    SignalListItemFactory, StringList, StringObject, ColorButton
from gi.repository.Adw import ActionRow, ComboRow, EntryRow, \
    ExpanderRow, PreferencesGroup, SwitchRow
from gi.repository import GLib

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import icon_helper, \
    service_parameters_helper, settings_helper, text_helper
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
    icon_icon: EntryRow
    icon_color: ColorButton
    icon_scale: ScaleRow
    icon_opacity: ScaleRow
    icon_custom_icon_expander: BetterExpander

    text_show_text: ExpanderRow
    text_attribute_combo: ComboRow
    text_round: ExpanderRow
    text_round_precision: ScaleRow
    text_text_size: ScaleRow
    text_text_color: ColorButton
    text_outline_size: ScaleRow
    text_outline_color: ColorButton
    text_attribute_model: StringList
    text_position_combo: ComboRow
    text_show_unit: SwitchRow
    text_unit_line_break: SwitchRow
    text_custom_text_expander: BetterExpander

    dial_entity_domain_combo: ComboRow
    dial_entity_domain_model: StringList

    dial_entity_entity_combo: ComboRow
    dial_entity_entity_model: StringList

    dial_service_call_service: ExpanderRow
    dial_service_service_combo: ComboRow
    dial_service_service_model: StringList

    dial_step_size: ScaleRow

    connection_status: ActionRow

    connect_rows: List = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.has_configuration = True

        # Timeout mechanism for dial turns
        self._accumulated_step: int = 0
        self._dial_timer: threading.Timer | None = None
        self.dial_timeout: float = 0.2  # 200ms timeout

        self.uuid = uuid.uuid4()

    def on_ready(self) -> None:
        """
        Set up action when StreamController has finished loading.
        """
        settings = settings_helper.migrate(self.get_settings())
        self.settings = settings_helper.get_action_settings(settings)
        self.set_settings(self.settings)

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
        # if Input.Dial > -1:
        dial_settings_group = self._get_dial_settings_group()

        self._load_attributes()
        self._load_icon_settings()
        self._load_custom_icons()
        self._load_custom_text()
        self._load_text_settings()

        self.initialized = True

        self._load_domains()
        self._load_dial_domains()

        self._set_enabled_disabled()

        # connect as the last action - else the on_change functions trigger on populating the models
        self._connect_rows()

        return [entity_group, service_group, icon_group, text_group, dial_settings_group, connection_group]

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

        #
        # Icon show icon
        #
        self.icon_show_icon = ExpanderRow(title=self.lm.get(const.LABEL_ICON_SHOW_ICON))
        self.icon_show_icon.set_show_enable_switch(True)
        self.connect_rows.append(
            partial(self.icon_show_icon.connect, const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                    self._on_change_expansion_switch,
                    const.SETTING_ICON_SHOW_ICON))

        #
        # Icon icon
        #
        self.icon_icon = EntryRow(title=self.lm.get(const.LABEL_ICON_ICON))
        self.connect_rows.append(
            partial(self.icon_icon.connect, const.CONNECT_NOTIFY_TEXT, self._on_change_entry,
                    const.SETTING_ICON_ICON))

        #
        # Icon icon color
        #
        self.icon_color = ColorButton()
        self.connect_rows.append(
            partial(self.icon_color.connect, const.CONNECT_NOTIFY_COLOR_SET, self._on_change_color,
                    const.SETTING_ICON_COLOR))

        icon_color_row = ActionRow(title=self.lm.get(const.LABEL_ICON_COLOR))
        icon_color_row.add_suffix(self.icon_color)

        #
        # Icon scale
        #
        self.icon_scale: ScaleRow = ScaleRow(self.lm.get(const.LABEL_ICON_SCALE),
                                             const.ICON_MIN_SCALE, const.ICON_MAX_SCALE, 1)
        self.connect_rows.append(
            partial(self.icon_scale.connect, const.CONNECT_VALUE_CHANGED, self._on_change_scale,
                    const.SETTING_ICON_SCALE))

        #
        # Icon opacity
        #
        self.icon_opacity: ScaleRow = ScaleRow(self.lm.get(const.LABEL_ICON_OPACITY),
                                               const.ICON_MIN_OPACITY, const.ICON_MAX_OPACITY, 1)
        self.connect_rows.append(
            partial(self.icon_opacity.connect, const.CONNECT_VALUE_CHANGED, self._on_change_scale,
                    const.SETTING_ICON_OPACITY))

        #
        # Icon custom icon
        #
        icon_custom_icon_add = Button(icon_name="list-add", valign=Align.CENTER)
        icon_custom_icon_add.set_size_request(15, 15)
        self.connect_rows.append(
            partial(icon_custom_icon_add.connect, const.CONNECT_CLICKED,
                    self._on_add_customization, const.CUSTOMIZATION_TYPE_ICON,
                    self._add_custom_icon))

        self.icon_custom_icon_expander = BetterExpander(
            title=self.lm.get(const.LABEL_ICON_CUSTOM_ICON))
        self.icon_custom_icon_expander.add_suffix(icon_custom_icon_add)

        self.icon_show_icon.add_row(self.icon_icon)
        self.icon_show_icon.add_row(icon_color_row)
        self.icon_show_icon.add_row(self.icon_scale)
        self.icon_show_icon.add_row(self.icon_opacity)
        self.icon_show_icon.add_row(self.icon_custom_icon_expander)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_ICON))
        group.set_margin_top(20)
        group.add(self.icon_show_icon)

        return group

    def _load_icon_settings(self):
        self.icon_show_icon.set_enable_expansion(self.settings[const.SETTING_ICON_SHOW_ICON])
        self.icon_icon.set_text(self.settings[const.SETTING_ICON_ICON])
        self.icon_color.set_rgba(
            helper.convert_color_list_to_rgba(self.settings[const.SETTING_ICON_COLOR]))
        self.icon_scale.set_value(self.settings[const.SETTING_ICON_SCALE])
        self.icon_opacity.set_value(self.settings[const.SETTING_ICON_OPACITY])

    def _add_custom_icon(self, attribute: str, operator: str, value: str, icon: str, color: str,
                         scale: int, opacity: int, index: int):
        customization = {
            const.CUSTOM_ATTRIBUTE: attribute,
            const.CUSTOM_OPERATOR: operator,
            const.CUSTOM_VALUE: value
        }

        if icon is not None:
            customization[const.CUSTOM_ICON_ICON] = icon

        if color is not None:
            customization[const.CUSTOM_ICON_COLOR] = color

        if scale is not None:
            customization[const.CUSTOM_ICON_SCALE] = scale

        if opacity is not None:
            customization[const.CUSTOM_ICON_OPACITY] = opacity

        custom_icons_to_check_for_duplicates = self.settings[
            const.SETTING_CUSTOMIZATION_ICON].copy()

        if index > -1:
            # we have to check for duplicates without the item being edited because it may have
            # not been changed
            custom_icons_to_check_for_duplicates.pop(index)

        if customization in custom_icons_to_check_for_duplicates:
            if index > -1:
                # edited item is identical to existing - delete it
                self.settings[const.SETTING_CUSTOMIZATION_ICON].pop(index)
                self.set_settings(self.settings)

            self._load_custom_icons()
            self._entity_updated()
            return

        if index > -1:
            self.settings[const.SETTING_CUSTOMIZATION_ICON][index] = customization
        else:
            self.settings[const.SETTING_CUSTOMIZATION_ICON].append(customization)

        self.set_settings(self.settings)
        self._load_custom_icons()
        self._entity_updated()

    def _get_text_group(self) -> PreferencesGroup:
        """
        Get all text rows.
        """

        #
        # Text show text
        #
        self.text_show_text = ExpanderRow(title=self.lm.get(const.LABEL_TEXT_SHOW_TEXT))
        self.text_show_text.set_show_enable_switch(True)
        self.connect_rows.append(
            partial(self.text_show_text.connect, const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                    self._on_change_expansion_switch,
                    const.SETTING_TEXT_SHOW_TEXT))

        #
        # Text position
        #
        text_position_model = StringList.new(
            [const.TEXT_POSITION_TOP, const.TEXT_POSITION_CENTER, const.TEXT_POSITION_BOTTOM])

        self.text_position_combo = ComboRow(title=self.lm.get(const.LABEL_TEXT_POSITION))
        self.text_position_combo.set_factory(self.combo_factory)
        self.text_position_combo.set_model(text_position_model)
        self.connect_rows.append(
            partial(self.text_position_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_combo,
                    const.SETTING_TEXT_POSITION))

        self.text_show_text.set_enable_expansion(self.settings[const.SETTING_TEXT_SHOW_TEXT])

        #
        # Text attribute
        #
        self.text_attribute_combo = ComboRow(title=self.lm.get(const.LABEL_TEXT_ATTRIBUTE))
        self.text_attribute_combo.set_factory(self.combo_factory)
        self.connect_rows.append(
            partial(self.text_attribute_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_combo,
                    const.SETTING_TEXT_ATTRIBUTE))

        #
        # Text round
        #
        self.text_round = ExpanderRow(title=self.lm.get(const.LABEL_TEXT_ROUND))
        self.text_round.set_show_enable_switch(True)
        self.connect_rows.append(
            partial(self.text_round.connect, const.CONNECT_NOTIFY_ENABLE_EXPANSION,
                    self._on_change_expansion_switch,
                    const.SETTING_TEXT_ROUND))

        #
        # Text round precision
        #
        self.text_round_precision = ScaleRow(self.lm.get(const.LABEL_TEXT_ROUND_PRECISION),
                                             const.TEXT_ROUND_MIN_PRECISION,
                                             const.TEXT_ROUND_MAX_PRECISION, 1)
        self.connect_rows.append(
            partial(self.text_round_precision.connect, const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale,
                    const.SETTING_TEXT_ROUND_PRECISION))

        self.text_round.add_row(self.text_round_precision)

        #
        # Text size
        #
        self.text_text_size = ScaleRow(self.lm.get(const.LABEL_TEXT_TEXT_SIZE),
                                       const.TEXT_TEXT_MIN_SIZE, const.TEXT_TEXT_MAX_SIZE, 1)
        self.connect_rows.append(
            partial(self.text_text_size.connect, const.CONNECT_VALUE_CHANGED, self._on_change_scale,
                    const.SETTING_TEXT_TEXT_SIZE))

        #
        # Text color
        #
        self.text_text_color = ColorButton()
        self.connect_rows.append(
            partial(self.text_text_color.connect, const.CONNECT_NOTIFY_COLOR_SET,
                    self._on_change_color,
                    const.SETTING_TEXT_TEXT_COLOR))

        text_color_row = ActionRow(title=self.lm.get(const.LABEL_TEXT_TEXT_COLOR))
        text_color_row.add_suffix(self.text_text_color)

        #
        # Text outline size
        #
        self.text_outline_size = ScaleRow(self.lm.get(const.LABEL_TEXT_OUTLINE_SIZE),
                                          const.TEXT_OUTLINE_MIN_SIZE, const.TEXT_OUTLINE_MAX_SIZE,
                                          1)
        self.connect_rows.append(
            partial(self.text_outline_size.connect, const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale,
                    const.SETTING_TEXT_OUTLINE_SIZE))

        #
        # Text outline color
        #
        self.text_outline_color = ColorButton()
        self.connect_rows.append(
            partial(self.text_outline_color.connect, const.CONNECT_NOTIFY_COLOR_SET,
                    self._on_change_color,
                    const.SETTING_TEXT_OUTLINE_COLOR))

        outline_color_row = ActionRow(title=self.lm.get(const.LABEL_TEXT_OUTLINE_COLOR))
        outline_color_row.add_suffix(self.text_outline_color)

        #
        # Text show unit
        #
        self.text_show_unit = SwitchRow(title=self.lm.get(const.LABEL_TEXT_SHOW_UNIT))
        self.connect_rows.append(partial(self.text_show_unit.connect, const.CONNECT_NOTIFY_ACTIVE,
                                         self._on_change_switch,
                                         const.SETTING_TEXT_SHOW_UNIT))

        #
        # Text unit line break
        #
        self.text_unit_line_break = SwitchRow(title=self.lm.get(const.LABEL_TEXT_UNIT_LINE_BREAK))
        self.connect_rows.append(
            partial(self.text_unit_line_break.connect, const.CONNECT_NOTIFY_ACTIVE,
                    self._on_change_switch,
                    const.SETTING_TEXT_UNIT_LINE_BREAK))

        #
        # Text custom text
        #
        text_custom_text_add = Button(icon_name="list-add", valign=Align.CENTER)
        text_custom_text_add.set_size_request(15, 15)
        self.connect_rows.append(
            partial(text_custom_text_add.connect, const.CONNECT_CLICKED,
                    self._on_add_customization, const.CUSTOMIZATION_TYPE_TEXT,
                    self._add_custom_text))

        self.text_custom_text_expander = BetterExpander(
            title=self.lm.get(const.LABEL_TEXT_CUSTOM_TEXT))
        self.text_custom_text_expander.add_suffix(text_custom_text_add)

        self.text_show_text.add_row(self.text_position_combo)
        self.text_show_text.add_row(self.text_attribute_combo)
        self.text_show_text.add_row(self.text_round)
        self.text_show_text.add_row(self.text_text_size)
        self.text_show_text.add_row(text_color_row)
        self.text_show_text.add_row(self.text_outline_size)
        self.text_show_text.add_row(outline_color_row)
        self.text_show_text.add_row(self.text_show_unit)
        self.text_show_text.add_row(self.text_unit_line_break)
        self.text_show_text.add_row(self.text_custom_text_expander)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_TEXT))
        group.set_margin_top(20)
        group.add(self.text_show_text)

        return group

    def _load_text_settings(self):
        self.text_show_text.set_enable_expansion(self.settings[const.SETTING_TEXT_SHOW_TEXT])
        helper.set_value_in_combo(self.text_position_combo,
                                  self.settings[const.SETTING_TEXT_POSITION])
        self.text_round.set_enable_expansion(self.settings[const.SETTING_TEXT_ROUND])
        self.text_round_precision.set_value(self.settings[const.SETTING_TEXT_ROUND_PRECISION])
        self.text_text_size.set_value(self.settings[const.SETTING_TEXT_TEXT_SIZE])
        self.text_text_color.set_rgba(
            helper.convert_color_list_to_rgba(self.settings[const.SETTING_TEXT_TEXT_COLOR]))
        self.text_outline_size.set_value(self.settings[const.SETTING_TEXT_OUTLINE_SIZE])
        self.text_outline_color.set_rgba(
            helper.convert_color_list_to_rgba(self.settings[const.SETTING_TEXT_OUTLINE_COLOR]))
        self.text_show_unit.set_active(self.settings[const.SETTING_TEXT_SHOW_UNIT])
        self.text_unit_line_break.set_active(self.settings[const.SETTING_TEXT_UNIT_LINE_BREAK])

    def _add_custom_text(self, attribute_for_operation: str, operator: str, value: str,
                         position: str, attribute: str, custom_text: str, text_round: bool,
                         round_precision: int,
                         text_size: int, text_color: List[int], outline_size: int,
                         outline_color: List[int], show_unit: bool, line_beak: bool, index: int):
        customization = {
            const.CUSTOM_ATTRIBUTE: attribute_for_operation,
            const.CUSTOM_OPERATOR: operator,
            const.CUSTOM_VALUE: value
        }

        if position is not None:
            customization[const.CUSTOM_TEXT_POSITION] = position

        if attribute is not None:
            customization[const.CUSTOM_TEXT_ATTRIBUTE] = attribute

        if custom_text is not None:
            customization[const.CUSTOM_TEXT_CUSTOM_TEXT] = custom_text

        if text_round is not None:
            customization[const.CUSTOM_TEXT_ROUND] = text_round

        if round_precision is not None:
            customization[const.CUSTOM_TEXT_ROUND_PRECISION] = round_precision

        if text_size is not None:
            customization[const.CUSTOM_TEXT_TEXT_SIZE] = text_size

        if text_color is not None:
            customization[const.CUSTOM_TEXT_TEXT_COLOR] = text_color

        if outline_size is not None:
            customization[const.CUSTOM_TEXT_OUTLINE_SIZE] = outline_size

        if outline_color is not None:
            customization[const.CUSTOM_TEXT_OUTLINE_COLOR] = outline_color

        if show_unit is not None:
            customization[const.CUSTOM_TEXT_SHOW_UNIT] = show_unit

        if line_beak is not None:
            customization[const.CUSTOM_TEXT_LINE_BREAK] = line_beak

        custom_text_to_check_for_duplicates = self.settings[
            const.SETTING_CUSTOMIZATION_TEXT].copy()

        if index > -1:
            # we have to check for duplicates without the item being edited because it may have
            # not been changed
            custom_text_to_check_for_duplicates.pop(index)

        if customization in custom_text_to_check_for_duplicates:
            if index > -1:
                # edited item is identical to existing - delete it
                self.settings[const.SETTING_CUSTOMIZATION_TEXT].pop(index)
                self.set_settings(self.settings)

            self._load_custom_text()
            self._entity_updated()
            return

        if index > -1:
            self.settings[const.SETTING_CUSTOMIZATION_TEXT][index] = customization
        else:
            self.settings[const.SETTING_CUSTOMIZATION_TEXT].append(customization)

        self.set_settings(self.settings)
        self._load_custom_text()
        self._entity_updated()

    def _get_connection_group(self) -> PreferencesGroup:
        """
        Get all connection rows.
        """

        #
        # Connection status
        #
        self.connection_status = ActionRow(title=self.lm.get(const.SETTING_CONNECTION_STATUS))
        self.connection_status.set_title(
            const.CONNECTED if self.plugin_base.backend.is_connected() else const.NOT_CONNECTED)

        self.plugin_base.backend.set_connection_status_callback(self.set_connection_status)

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_CONNECTION))
        group.set_margin_top(20)
        group.add(self.connection_status)

        return group

    def _get_dial_settings_group(self) -> PreferencesGroup:
        """
        Get all dial entity rows.
        """
        self.dial_entity_domain_combo = ComboRow(title=self.lm.get(const.LABEL_ENTITY_DOMAIN))
        self.dial_entity_domain_combo.set_enable_search(True)
        self.dial_entity_domain_combo.set_expression(self.combo_expression)
        self.connect_rows.append(
            partial(self.dial_entity_domain_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_dial_domain))

        self.dial_entity_entity_combo = ComboRow(title=self.lm.get(const.LABEL_ENTITY_ENTITY))
        self.dial_entity_entity_combo.set_factory(self.combo_factory)
        self.dial_entity_entity_combo.set_enable_search(True)
        self.dial_entity_entity_combo.set_expression(self.combo_expression)
        self.connect_rows.append(
            partial(self.dial_entity_entity_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_dial_entity))

        self.dial_service_service_combo = ComboRow(title=self.lm.get(const.LABEL_SERVICE_SERVICE))
        self.dial_service_service_combo.set_factory(self.combo_factory)
        self.dial_service_service_combo.set_enable_search(True)
        self.dial_service_service_combo.set_expression(self.combo_expression)
        self.connect_rows.append(
            partial(self.dial_service_service_combo.connect, const.CONNECT_NOTIFY_SELECTED,
                    self._on_change_dial_service))

        self.dial_step_size = ScaleRow(self.lm.get(const.LABEL_TEXT_TEXT_SIZE),
                                       const.DIAL_STEP_SIZE_MIN_SIZE, const.DIAL_STEP_SIZE_MAX_SIZE, 1)
        self.connect_rows.append(
            partial(self.dial_step_size.connect, const.CONNECT_VALUE_CHANGED, self._on_change_dial_step_size,
                    const.SETTING_DIAL_STEP_SIZE))

        group = PreferencesGroup()
        group.set_title(self.lm.get(const.LABEL_SETTINGS_DIAL))
        group.set_margin_top(20)
        group.add(self.dial_entity_domain_combo)
        group.add(self.dial_entity_entity_combo)
        group.add(self.dial_service_service_combo)
        group.add(self.dial_step_size)

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

            self.settings = settings_helper.get_action_settings(
                {const.SETTING_ENTITY_DOMAIN: domain})
            self.set_settings(self.settings)

            self.entity_entity_combo.set_model(None)
            self.service_service_combo.set_model(None)
            self.set_media()

            self._load_icon_settings()
            self._load_text_settings()


        if domain:
            self._load_entities()
            self._load_services()

        self._set_enabled_disabled()

    def _on_change_dial_domain(self, combo, _):
        """
        Execute when the domain is changed.
        """
        old_domain = self.settings.setdefault(const.SETTING_DIAL_ENTITY_DOMAIN, const.EMPTY_STRING)

        domain = combo.get_selected_item().get_string()

        self.set_setting(const.SETTING_DIAL_ENTITY_DOMAIN, domain)

        if old_domain != domain:
            self.dial_entity_entity_combo.set_model(None)
            self.dial_service_service_combo.set_model(None)

        if domain:
            self._load_dial_entities()
            self._load_dial_services()

    def _on_change_entity(self, combo, _):
        """
        Execute when the entity is changed.
        """
        old_entity = self.settings[const.SETTING_ENTITY_ENTITY]
        entity = combo.get_selected_item().get_string()

        if old_entity == entity:
            return

        self.set_setting(const.SETTING_ENTITY_ENTITY, entity)

        if old_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, self.uuid)

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.uuid, self._entity_updated)

            self._load_attributes()
            service_parameters_helper.load_service_parameters(self)

        self._entity_updated()

        self._set_enabled_disabled()

    def _on_change_dial_entity(self, combo, _):
        """
        Execute when the entity is changed.
        """
        old_entity = self.settings[const.SETTING_DIAL_ENTITY_ENTITY]
        entity = combo.get_selected_item().get_string()

        if old_entity == entity:
            return

        self.set_setting(const.SETTING_DIAL_ENTITY_ENTITY, entity)

    def _on_change_service(self, combo, _):
        """
        Execute when the service is changed.
        """
        value = combo.get_selected_item().get_string() if combo.get_selected_item() else ""
        self.set_setting(const.SETTING_SERVICE_SERVICE, value)
        self.set_setting(const.SETTING_SERVICE_PARAMETERS, {})

        service_parameters_helper.load_service_parameters(self)

        self._set_enabled_disabled()

        self._entity_updated()

    def _on_change_dial_service(self, combo, _):
        """
        Execute when the service is changed.
        """
        value = combo.get_selected_item().get_string() if combo.get_selected_item() else ""
        self.set_setting(const.SETTING_DIAL_SERVICE_SERVICE, value)

    def _on_change_combo(self, combo, *args):
        """
        Execute when a new selection is made in a combo row.
        """
        value = combo.get_selected_item().get_string()
        self.set_setting(args[1], value)

        self._set_enabled_disabled()

        self._entity_updated()

    def _on_change_spin(self, spin, *args):
        """
        Execute when the number is changed in a spin row.
        """
        size = spin.get_value()
        self.set_setting(args[0], size)

        self._entity_updated()

    def _on_change_scale(self, scale, *args):
        """
        Execute when the value is changed in a scale.
        """
        size = scale.get_value()
        self.set_setting(args[1], size)

        self._entity_updated()

    def _on_change_dial_step_size(self, scale, *_):
        """
        Execute when the value is changed in a scale.
        """
        size = scale.get_value()
        self.set_setting(const.SETTING_DIAL_STEP_SIZE, size)

    def _on_change_spin_event_controller(self, _, *args):
        """
        Execute when the number is changed in a spin row.
        """
        size = args[0].get_value()
        self.set_setting(args[1], size)

        self._entity_updated()

    def _entity_updated(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        show_icon = self.settings[const.SETTING_ICON_SHOW_ICON]
        show_text = self.settings[const.SETTING_TEXT_SHOW_TEXT]

        if not show_icon and not show_text:
            self.set_media()
            self._clear_labels()
            return

        entity = self.settings[const.SETTING_ENTITY_ENTITY]

        if (show_icon or show_text) and state is None:
            state = self.plugin_base.backend.get_entity(entity)

        self._update_icon(show_icon, state)
        self._update_labels(show_text, state)

        if self.initialized:
            self._load_custom_icons()
            self._load_custom_text()
            self._set_enabled_disabled()

    def _dial_entity_updated(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        show_icon = self.settings[const.SETTING_ICON_SHOW_ICON]
        show_text = self.settings[const.SETTING_TEXT_SHOW_TEXT]

        if not show_icon and not show_text:
            self.set_media()
            self._clear_labels()
            return

        entity = self.settings[const.SETTING_DIAL_ENTITY_ENTITY]

        if (show_icon or show_text) and state is None:
            state = self.plugin_base.backend.get_entity(entity)

        self._update_icon(show_icon, state)
        self._update_labels(show_text, state)

        if self.initialized:
            self._load_custom_icons()
            self._load_custom_text()
            self._set_enabled_disabled()

    def _update_icon(self, show_icon: bool, state: dict):
        """
        Update the icon to reflect the entity state.
        """
        if not show_icon or not state:
            self.set_media()
            return

        icon, scale = icon_helper.get_icon(state, self.settings)

        self.set_media(media_path=icon, size=scale)

    def _update_labels(self, show_text: bool, state: dict):
        """
        Update the labels to reflect the entity state.
        """
        self._clear_labels()

        if not show_text or not state:
            return

        text, position, text_size, text_color, outline_size, outline_color = text_helper.get_text(
            state, self.settings)

        self.set_label(text, position, text_color, None, text_size, outline_size, outline_color,
                       None, None, True)

    def _clear_labels(self):
        self.set_top_label(const.EMPTY_STRING)
        self.set_center_label(const.EMPTY_STRING)
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

        helper.set_value_in_combo(self.entity_domain_combo, old_domain)
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

        helper.set_value_in_combo(self.entity_entity_combo, old_entity)

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

        helper.set_value_in_combo(self.service_service_combo, old_service)
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

        helper.set_value_in_combo(self.text_attribute_combo, old_attribute)

    def _load_custom_icons(self):
        self.icon_custom_icon_expander.clear()

        attributes = [self.text_attribute_model.get_string(i) for i in
                      range(len(self.text_attribute_model))]
        state = self.plugin_base.backend.get_entity(self.settings[const.SETTING_ENTITY_ENTITY])

        for index, customization in enumerate(self.settings[const.SETTING_CUSTOMIZATION_ICON]):
            row = CustomizationIconRow(self.lm, customization,
                                       self.settings[const.SETTING_CUSTOMIZATION_ICON], index,
                                       attributes, state, self.settings)

            row.edit_button.connect(const.CONNECT_CLICKED, self._on_add_customization,
                                    const.CUSTOMIZATION_TYPE_ICON, self._add_custom_icon,
                                    self.settings[const.SETTING_CUSTOMIZATION_ICON], index)

            row.delete_button.connect(const.CONNECT_CLICKED, self._on_delete_customization,
                                      self.settings[const.SETTING_CUSTOMIZATION_ICON], index)

            row.up_button.connect(const.CONNECT_CLICKED, self._on_move_up,
                                  self.settings[const.SETTING_CUSTOMIZATION_ICON], index)

            row.down_button.connect(const.CONNECT_CLICKED, self._on_move_down,
                                    self.settings[const.SETTING_CUSTOMIZATION_ICON], index)

            self.icon_custom_icon_expander.add_row(row)

    def _load_custom_text(self):
        self.text_custom_text_expander.clear()

        attributes = [self.text_attribute_model.get_string(i) for i in
                      range(len(self.text_attribute_model))]
        state = self.plugin_base.backend.get_entity(self.settings[const.SETTING_ENTITY_ENTITY])

        for index, customization in enumerate(self.settings[const.SETTING_CUSTOMIZATION_TEXT]):
            row = CustomizationTextRow(self.lm, customization,
                                       self.settings[const.SETTING_CUSTOMIZATION_TEXT], index,
                                       attributes, state, self.settings)

            row.edit_button.connect(const.CONNECT_CLICKED, self._on_add_customization,
                                    const.CUSTOMIZATION_TYPE_TEXT, self._add_custom_text,
                                    self.settings[const.SETTING_CUSTOMIZATION_TEXT], index)

            row.delete_button.connect(const.CONNECT_CLICKED, self._on_delete_customization,
                                      self.settings[const.SETTING_CUSTOMIZATION_TEXT], index)

            row.up_button.connect(const.CONNECT_CLICKED, self._on_move_up,
                                  self.settings[const.SETTING_CUSTOMIZATION_TEXT], index)

            row.down_button.connect(const.CONNECT_CLICKED, self._on_move_down,
                                    self.settings[const.SETTING_CUSTOMIZATION_TEXT], index)

            self.text_custom_text_expander.add_row(row)

    def _load_dial_domains(self):
        """
        Load domains from Home Assistant.
        """
        old_domain = self.settings[const.SETTING_DIAL_ENTITY_DOMAIN]

        self.dial_entity_domain_model = StringList.new([const.EMPTY_STRING])
        self.dial_entity_domain_combo.set_model(self.dial_entity_domain_model)

        all_domains = self.plugin_base.backend.get_domains()
        domains = [domain for domain in const.DIAL_ALLOWED_DOMAINS if domain in all_domains]

        if not old_domain in domains:
            domains.append(old_domain)

        for domain in domains:
            self.dial_entity_domain_model.append(domain)

        helper.set_value_in_combo(self.dial_entity_domain_combo, old_domain)
        self._load_dial_entities()
        self._load_dial_services()

    def _load_dial_entities(self):
        """
        Load entities from Home Assistant.
        """
        old_entity = self.settings[const.SETTING_DIAL_ENTITY_ENTITY]

        self.dial_entity_entity_model = StringList.new([const.EMPTY_STRING])
        self.dial_entity_entity_combo.set_model(self.dial_entity_entity_model)

        entities = sorted(
            self.plugin_base.backend.get_entities(
                self.dial_entity_domain_combo.get_selected_item().get_string()))

        if not old_entity in entities:
            entities.append(old_entity)

        for entity in entities:
            self.dial_entity_entity_model.append(entity)

        helper.set_value_in_combo(self.dial_entity_entity_combo, old_entity)

    def _load_dial_services(self):
        """
        Load services from Home Assistant.
        """
        old_service = self.settings[const.SETTING_DIAL_SERVICE_SERVICE]

        self.dial_service_service_model = StringList.new([])
        self.dial_service_service_combo.set_model(self.dial_service_service_model)
        self.dial_step_size.set_value(self.settings[const.SETTING_DIAL_STEP_SIZE])

        all_domains = self.plugin_base.backend.get_domains()

        all_services = self.plugin_base.backend.get_services(
            self.dial_entity_domain_combo.get_selected_item().get_string())
        services = [service for service in const.DIAL_ALLOWED_SERVICES if service in all_services]

        for service in services:
            self.dial_service_service_model.append(service)

        helper.set_value_in_combo(self.dial_service_service_combo, old_service)

    def _on_add_customization(self, _, customization_type: str, callback,
                              customization_list: List = None, index: int = -1):
        attributes = [self.text_attribute_model.get_string(i) for i in
                      range(len(self.text_attribute_model))]

        current = None

        if customization_list and index > -1:
            current = customization_list[index]

        if customization_type == const.CUSTOMIZATION_TYPE_ICON:
            window = CustomizationIconWindow(self.lm, attributes, callback, current=current,
                                             index=index)
        elif customization_type == const.CUSTOMIZATION_TYPE_TEXT:
            window = CustomizationTextWindow(self.lm, attributes, callback, current=current,
                                             index=index)
        else:
            raise ValueError(f"Unknown customization type: {customization_type}")

        window.show()

    def _on_delete_customization(self, _, customization_list: List, index: int):
        customization_list.pop(index)
        self.set_settings(self.settings)

        self._load_custom_icons()
        self._load_custom_text()

        self._entity_updated()

    def _on_move_up(self, _, customization_list: List, index: int):
        customization_list[index], customization_list[index - 1] = customization_list[index - 1], \
            customization_list[index]
        self.set_settings(self.settings)

        self._load_custom_icons()
        self._load_custom_text()

        self._entity_updated()

    def _on_move_down(self, _, customization_list: List, index: int):
        customization_list[index], customization_list[index + 1] = customization_list[index + 1], \
            customization_list[index]
        self.set_settings(self.settings)

        self._load_custom_icons()
        self._load_custom_text()

        self._entity_updated()

    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
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
            self.icon_custom_icon_expander.set_expanded(
                len(self.settings[const.SETTING_CUSTOMIZATION_ICON]) > 0)

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

            self.text_custom_text_expander.set_expanded(
                len(self.settings[const.SETTING_CUSTOMIZATION_TEXT]) > 0)

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

    def event_callback(self, event: InputEvent, data: dict) -> None:
        """
        Callback for dial events.
        """
        if event == Input.Dial.Events.TURN_CW:
            if self.settings[const.SETTING_DIAL_SERVICE_SERVICE]:
                self._accumulate_dial_step(self.settings[const.SETTING_DIAL_STEP_SIZE])
            else:
                print("DialAction: Dial turned clockwise, but no turn service configured.")
        
        elif event == Input.Dial.Events.TURN_CCW:
            if self.settings[const.SETTING_DIAL_SERVICE_SERVICE]:
                self._accumulate_dial_step(-self.settings[const.SETTING_DIAL_STEP_SIZE])
            else:
                print("DialAction: Dial turned counter-clockwise, but no turn service configured.")
        
        else:
            super().event_callback(event, data)

    def _accumulate_dial_step(self, step: int) -> None:
        """
        Accumulate dial steps and set/reset timer for delayed service call.
        """
        # Cancel existing timer if running
        if self._dial_timer is not None:
            self._dial_timer.cancel()
        
        # Accumulate the step
        self._accumulated_step += step
        
        # Start new timer
        self._dial_timer = threading.Timer(self.dial_timeout, self._execute_accumulated_dial_turn)
        self._dial_timer.start()
        
    def _execute_accumulated_dial_turn(self) -> None:
        """
        Execute the accumulated dial turn service call.
        """
        if self._accumulated_step == 0:
            return
        
        try:
            full_service = f"{self.settings[const.SETTING_DIAL_ENTITY_DOMAIN]}.{self.settings[const.SETTING_DIAL_SERVICE_SERVICE]}"
            _domain, service_name = full_service.split('.', 1)
            service_data = {
                "entity_id": self.settings[const.SETTING_DIAL_ENTITY_ENTITY],
                "brightness_step_pct": self._accumulated_step
            }
            
            self.plugin_base.backend.call_service(self.settings[const.SETTING_DIAL_ENTITY_ENTITY], service_name, service_data)
            
        except ValueError:
            print(f"DialAction: Invalid service format for dial_turn_service: {service_name}. Expected 'domain.service_name'.")
        except Exception as e:
            print(f"DialAction: Error calling accumulated service {self.settings[const.SETTING_DIAL_SERVICE_SERVICE]} on {self.settings[const.SETTING_DIAL_ENTITY_ENTITY]}: {e}")
        finally:
            # Reset accumulated step and timer
            self._accumulated_step = 0
            self._dial_timer = None

