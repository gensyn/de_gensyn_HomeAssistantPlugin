"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import json
from collections import Counter
from json import JSONDecodeError
from typing import List, Tuple

import gi
gi.require_version("Adw", "1")
from gi.repository.Gtk import Button, Align, Widget
from gi.repository.Adw import PreferencesGroup


from GtkHelper.GenerativeUI.ColorButtonRow import ColorButtonRow
from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.GenerativeUI.EntryRow import EntryRow
from GtkHelper.GenerativeUI.ExpanderRow import ExpanderRow
from GtkHelper.GenerativeUI.ScaleRow import ScaleRow
from GtkHelper.GenerativeUI.SwitchRow import SwitchRow
from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.icon_customization import IconCustomization
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_icon_row import \
    CustomizationIconRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.row.customization_text_row import \
    CustomizationTextRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.text_customization import TextCustomization
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.window.customization_icon_window import \
    CustomizationIconWindow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.window.customization_text_window import \
    CustomizationTextWindow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import icon_helper, \
    text_helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.service_parameters import service_parameters_helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.settings.settings import Settings
from src.backend.PluginManager.ActionBase import ActionBase


class HomeAssistantAction(ActionBase):
    """
    Action to be loaded by StreamController.
    """
    settings: Settings

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # event_assigner = EventAssigner(
        #     id="Key Down",
        #     ui_label="Call service",
        #     default_event=Input.Key.Events.DOWN,
        #     callback=self._call_service
        # )
        #
        # self.add_event_assigner(event_assigner)

        self.initialized = False
        self.lm = self.plugin_base.locale_manager

        self._init_entity_group()
        self._init_service_group()
        self._init_icon_group()
        self._init_text_group()

        self.has_configuration = True

    def on_ready(self) -> None:
        """
        Set up action when StreamController has finished loading.
        """
        self.settings = Settings(self)

        if not self.plugin_base.backend.is_connected():
            self.plugin_base.backend.register_action(self.on_ready)

        entity = self.settings.get_entity()

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.settings.get_uuid(), self._entity_updated)

        self._load_domains()
        self._load_entities()
        self._load_services()
        self._load_attributes()
        self._load_icon_settings()
        self._load_custom_icons()
        self._load_custom_text()
        self._load_text_settings()

        self.initialized = True

        self._reload()

    def on_remove(self) -> None:
        """
        Clean up after action was removed.
        """
        self.plugin_base.backend.remove_action(self.on_ready)
        self.plugin_base.backend.remove_tracked_entity(
            self.settings.get_entity(),
            self.settings.get_uuid())

        self._entity_updated()

    def on_key_down(self) -> None:
        """
        Call the service stated in the settings.
        """
        entity = self.settings.get_entity()
        service = self.settings.get_service()

        if not entity or not service:
            return

        parameters = {}

        for parameter, value in self.settings.get_service_parameters().items():
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
        return [self._entity_group, self._service_group, self._icon_group, self._text_group]

    def _init_entity_group(self):
        """
        Get all entity rows.
        """
        self.entity_domain_combo: ComboRow = ComboRow(self, const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING, [],
                                                      const.LABEL_ENTITY_DOMAIN, enable_search=True,
                                                      on_change=self._on_change_domain, can_reset=False,
                                                      complex_var_name=True)

        self.entity_entity_combo: ComboRow = ComboRow(self, const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING, [],
                                                      const.LABEL_ENTITY_ENTITY, enable_search=True,
                                                      on_change=self._on_change_entity, can_reset=False,
                                                      complex_var_name=True)

        self._entity_group = self._create_group(const.LABEL_SETTINGS_ENTITY,
                                                [self.entity_domain_combo.widget, self.entity_entity_combo.widget])

    def _init_service_group(self):
        """
        Get all service rows.
        """
        self.service_call_service: ExpanderRow = ExpanderRow(self, const.SETTING_SERVICE_CALL_SERVICE,
                                                             const.DEFAULT_SERVICE_CALL_SERVICE,
                                                             title=const.LABEL_SERVICE_CALL_SERVICE,
                                                             show_enable_switch=True, on_change=self._reload,
                                                             can_reset=False, complex_var_name=True)

        self.service_service_combo: ComboRow = ComboRow(self, const.SETTING_SERVICE_SERVICE, const.EMPTY_STRING, [],
                                                        const.LABEL_SERVICE_SERVICE, enable_search=True,
                                                        on_change=self._on_change_service, can_reset=False,
                                                        complex_var_name=True)

        self.service_parameters: ExpanderRow = ExpanderRow(self, const.EMPTY_STRING, False,
                                                           title=const.LABEL_SERVICE_PARAMETERS, can_reset=False,
                                                           auto_add=False)

        self.service_call_service.add_row(self.service_service_combo.widget)
        self.service_call_service.add_row(self.service_parameters.widget)

        self._service_group = self._create_group(const.LABEL_SETTINGS_SERVICE, [self.service_call_service.widget])

    def _init_icon_group(self):
        """
        Get all icon rows.
        """

        #
        # Icon show icon
        #
        self.icon_show_icon: ExpanderRow = ExpanderRow(self, const.SETTING_ICON_SHOW_ICON, const.DEFAULT_ICON_SHOW_ICON,
                                                       title=const.LABEL_ICON_SHOW_ICON, show_enable_switch=True,
                                                       on_change=self._reload, can_reset=False, complex_var_name=True)

        #
        # Icon icon
        #
        self.icon_icon: EntryRow = EntryRow(self, const.SETTING_ICON_ICON, const.EMPTY_STRING,
                                            title=const.LABEL_ICON_ICON, on_change=self._reload, can_reset=False,
                                            complex_var_name=True)

        #
        # Icon icon color
        #
        self.icon_color: ColorButtonRow = ColorButtonRow(self, const.SETTING_ICON_COLOR, const.DEFAULT_ICON_COLOR,
                                                         title=const.LABEL_ICON_COLOR, on_change=self._reload,
                                                         can_reset=False, complex_var_name=True)

        #
        # Icon scale
        #
        self.icon_scale: ScaleRow = ScaleRow(self, const.SETTING_ICON_SCALE, const.DEFAULT_ICON_SCALE,
                                             const.ICON_MIN_SCALE, const.ICON_MAX_SCALE, title=const.LABEL_ICON_SCALE,
                                             step=1, digits=0, on_change=self._reload, can_reset=False,
                                             complex_var_name=True)

        #
        # Icon opacity
        #
        self.icon_opacity: ScaleRow = ScaleRow(self, const.SETTING_ICON_OPACITY, const.DEFAULT_ICON_OPACITY,
                                               const.ICON_MIN_OPACITY, const.ICON_MAX_OPACITY,
                                               title=const.LABEL_ICON_OPACITY, step=1, digits=0, on_change=self._reload,
                                               can_reset=False, complex_var_name=True)

        #
        # Icon custom icon
        #
        icon_custom_icon_add = Button(icon_name="list-add", valign=Align.CENTER)
        icon_custom_icon_add.set_size_request(15, 15)
        icon_custom_icon_add.connect(const.CONNECT_CLICKED,
                                     self._on_add_customization, const.CUSTOMIZATION_TYPE_ICON,
                                     self._add_custom_icon)

        self.icon_custom_icon_expander: ExpanderRow = ExpanderRow(self, const.EMPTY_STRING, False,
                                                                  title=const.LABEL_ICON_CUSTOM_ICON, can_reset=False,
                                                                  auto_add=False)
        self.icon_custom_icon_expander.widget.add_suffix(icon_custom_icon_add)

        self.icon_show_icon.add_row(self.icon_icon.widget)
        self.icon_show_icon.add_row(self.icon_color.widget)
        self.icon_show_icon.add_row(self.icon_scale.widget)
        self.icon_show_icon.add_row(self.icon_opacity.widget)
        self.icon_show_icon.add_row(self.icon_custom_icon_expander.widget)

        self._icon_group = self._create_group(const.LABEL_SETTINGS_ICON, [self.icon_show_icon.widget])

    def _init_text_group(self):
        """
        Get all text rows.
        """

        #
        # Text show text
        #
        self.text_show_text: ExpanderRow = ExpanderRow(self, const.SETTING_TEXT_SHOW_TEXT, const.DEFAULT_TEXT_SHOW_TEXT,
                                                       title=const.LABEL_TEXT_SHOW_TEXT, show_enable_switch=True,
                                                       on_change=self._reload, can_reset=False, complex_var_name=True)

        #
        # Text position
        #
        text_position_model = [const.TEXT_POSITION_TOP, const.TEXT_POSITION_CENTER, const.TEXT_POSITION_BOTTOM]

        self.text_position_combo: ComboRow = ComboRow(self, const.SETTING_TEXT_POSITION, const.TEXT_POSITION_CENTER,
                                                      text_position_model, const.LABEL_TEXT_POSITION,
                                                      on_change=self._reload, can_reset=False, complex_var_name=True)

        #
        # Text attribute
        #
        self.text_attribute_combo: ComboRow = ComboRow(self, const.SETTING_TEXT_ATTRIBUTE, const.DEFAULT_TEXT_ATTRIBUTE,
                                                       [], const.LABEL_TEXT_ATTRIBUTE, on_change=self._reload,
                                                       can_reset=False, complex_var_name=True)

        #
        # Text round
        #
        self.text_round: ExpanderRow = ExpanderRow(self, const.SETTING_TEXT_ROUND, const.DEFAULT_TEXT_ROUND,
                                                   title=const.LABEL_TEXT_ROUND, show_enable_switch=True,
                                                   on_change=self._reload, can_reset=False, complex_var_name=True)

        #
        # Text round precision
        #
        self.text_round_precision: ScaleRow = ScaleRow(self, const.SETTING_TEXT_ROUND_PRECISION,
                                                       const.DEFAULT_TEXT_ROUND_PRECISION,
                                                       const.TEXT_ROUND_MIN_PRECISION, const.TEXT_ROUND_MAX_PRECISION,
                                                       title=const.LABEL_TEXT_ROUND, step=1, digits=0,
                                                       on_change=self._reload, can_reset=False, complex_var_name=True)

        self.text_round.add_row(self.text_round_precision.widget)

        #
        # Text size
        #
        self.text_text_size: ScaleRow = ScaleRow(self, const.SETTING_TEXT_TEXT_SIZE, const.DEFAULT_TEXT_TEXT_SIZE,
                                                 const.TEXT_TEXT_MIN_SIZE, const.TEXT_TEXT_MAX_SIZE,
                                                 title=const.LABEL_TEXT_TEXT_SIZE, step=1, digits=0,
                                                 on_change=self._reload, can_reset=False, complex_var_name=True)

        #
        # Text color
        #
        self.text_text_color: ColorButtonRow = ColorButtonRow(self, const.SETTING_TEXT_TEXT_COLOR,
                                                              const.DEFAULT_TEXT_TEXT_COLOR,
                                                              title=const.LABEL_TEXT_TEXT_COLOR, on_change=self._reload,
                                                              can_reset=False, complex_var_name=True)

        #
        # Text outline size
        #
        self.text_outline_size: ScaleRow = ScaleRow(self, const.SETTING_TEXT_OUTLINE_SIZE,
                                                    const.DEFAULT_TEXT_OUTLINE_SIZE, const.TEXT_OUTLINE_MIN_SIZE,
                                                    const.TEXT_OUTLINE_MAX_SIZE, title=const.LABEL_TEXT_OUTLINE_SIZE,
                                                    step=1, digits=0, on_change=self._reload, can_reset=False,
                                                    complex_var_name=True)

        #
        # Text outline color
        #
        self.text_outline_color: ColorButtonRow = ColorButtonRow(self, const.SETTING_TEXT_OUTLINE_COLOR,
                                                                 const.DEFAULT_TEXT_OUTLINE_COLOR,
                                                                 title=const.LABEL_TEXT_OUTLINE_COLOR,
                                                                 on_change=self._reload, can_reset=False,
                                                                 complex_var_name=True)

        #
        # Text show unit
        #
        self.text_show_unit: SwitchRow = SwitchRow(self, const.SETTING_TEXT_SHOW_UNIT, const.DEFAULT_TEXT_SHOW_UNIT,
                                                   title=const.LABEL_TEXT_SHOW_UNIT, on_change=self._reload,
                                                   can_reset=False, complex_var_name=True)

        #
        # Text unit line break
        #
        self.text_unit_line_break: SwitchRow = SwitchRow(self, const.SETTING_TEXT_UNIT_LINE_BREAK,
                                                         const.DEFAULT_TEXT_UNIT_LINE_BREAK,
                                                         title=const.LABEL_TEXT_UNIT_LINE_BREAK, on_change=self._reload,
                                                         can_reset=False, complex_var_name=True)

        #
        # Text custom text
        #
        text_custom_text_add = Button(icon_name="list-add", valign=Align.CENTER)
        text_custom_text_add.set_size_request(15, 15)
        text_custom_text_add.connect(const.CONNECT_CLICKED,
                                     self._on_add_customization, const.CUSTOMIZATION_TYPE_TEXT,
                                     self._add_custom_text)

        self.text_custom_text_expander: ExpanderRow = ExpanderRow(self, const.EMPTY_STRING, False,
                                                                  title=const.LABEL_TEXT_CUSTOM_TEXT, can_reset=False,
                                                                  auto_add=False)
        self.text_custom_text_expander.widget.add_suffix(text_custom_text_add)

        self.text_show_text.add_row(self.text_position_combo.widget)
        self.text_show_text.add_row(self.text_attribute_combo.widget)
        self.text_show_text.add_row(self.text_round.widget)
        self.text_show_text.add_row(self.text_text_size.widget)
        self.text_show_text.add_row(self.text_text_color.widget)
        self.text_show_text.add_row(self.text_outline_size.widget)
        self.text_show_text.add_row(self.text_outline_color.widget)
        self.text_show_text.add_row(self.text_show_unit.widget)
        self.text_show_text.add_row(self.text_unit_line_break.widget)
        self.text_show_text.add_row(self.text_custom_text_expander.widget)

        self._text_group = self._create_group(const.LABEL_SETTINGS_TEXT, [self.text_show_text.widget])

    def _create_group(self, title_const: str, widgets: List[Widget]) -> PreferencesGroup:
        group = PreferencesGroup()
        group.set_title(self.lm.get(title_const))
        group.set_margin_top(20)

        for widget in widgets:
            group.add(widget)

        return group

    def _load_icon_settings(self):
        self.icon_show_icon.set_enable_expansion(self.settings.get_show_icon())
        self.icon_icon.set_text(self.settings.get_icon())
        self.icon_color.set_value(self.settings.get_icon_color())
        self.icon_scale.set_value(self.settings.get_icon_scale())
        self.icon_opacity.set_value(self.settings.get_icon_opacity())

    def _add_custom_icon(self, attribute: str, operator: str, value: str, icon: str, color: Tuple[int, int, int, int],
                         scale: int, opacity: int, index: int):
        customization = IconCustomization(attribute, operator, value, icon, color, scale, opacity)

        custom_icons_to_check_for_duplicates = self.settings.get_icon_customizations().copy()

        if index > -1:
            # we have to check for duplicates without the item being edited because it may have
            # not been changed
            custom_icons_to_check_for_duplicates.pop(index)

        if customization in custom_icons_to_check_for_duplicates:
            if index > -1:
                # edited item is identical to existing - delete it
                self.settings.remove_icon_customization(index)

            self._load_custom_icons()
            self._entity_updated()
            return

        if index > -1:
            self.settings.replace_icon_customization(index, customization)
        else:
            self.settings.add_icon_customization(customization)

        self._load_custom_icons()
        self._entity_updated()

    def _load_text_settings(self):
        self.text_show_text.set_enable_expansion(self.settings.get_show_text())
        self.text_position_combo.set_selected_item(self.settings.get_text_position())
        self.text_round.set_enable_expansion(self.settings.get_text_round())
        self.text_round_precision.set_value(self.settings.get_text_round_precision())
        self.text_text_size.set_value(self.settings.get_text_text_size())
        self.text_text_color.set_value(self.settings.get_text_text_color())
        self.text_outline_size.set_value(self.settings.get_text_outline_size())
        self.text_outline_color.set_value(self.settings.get_text_outline_color())
        self.text_show_unit.set_active(self.settings.get_text_show_unit())
        self.text_unit_line_break.set_active(self.settings.get_text_unit_line_break())

    def _add_custom_text(self, attribute: str, operator: str, value: str,
                         position: str, text_attribute: str, custom_text: str, text_round: bool,
                         round_precision: int,
                         text_size: int, text_color: Tuple[int, int, int, int], outline_size: int,
                         outline_color: Tuple[int, int, int, int], show_unit: bool, line_beak: bool, index: int):
        customization = TextCustomization(attribute, operator, value, position, text_attribute, custom_text, text_round,
                                          round_precision, text_size, text_color, outline_size, outline_color,
                                          show_unit, line_beak)

        custom_text_to_check_for_duplicates = self.settings.get_text_customizations().copy()

        if index > -1:
            # we have to check for duplicates without the item being edited because it may have
            # not been changed
            custom_text_to_check_for_duplicates.pop(index)

        if customization in custom_text_to_check_for_duplicates:
            if index > -1:
                # edited item is identical to existing - delete it
                self.settings.remove_text_customization(index)

            self._load_custom_text()
            self._entity_updated()
            return

        if index > -1:
            self.settings.replace_text_customization(index, customization)
        else:
            self.settings.add_text_customization(customization)

        self._load_custom_text()
        self._entity_updated()

    def _reload(self, *_):
        self._set_enabled_disabled()
        self._entity_updated()

    def _on_change_domain(self, _, domain, old_domain):
        """
        Execute when the domain is changed.
        """
        if not self.initialized:
            return

        domain = str(domain) if domain is not None else None
        old_domain = str(old_domain) if old_domain is not None else None

        if old_domain != domain:
            entity = self.settings.get_entity()

            if entity:
                self.plugin_base.backend.remove_tracked_entity(entity, self.settings.get_uuid())

            self.settings.reset(domain)

            self.entity_entity_combo.remove_all_items()
            self.service_service_combo.remove_all_items()
            self.set_media()

            self._load_icon_settings()
            self._load_text_settings()

        if domain:
            self._load_entities()
            self._load_services()

        self._set_enabled_disabled()

    def _on_change_entity(self, _, entity, old_entity):
        """
        Execute when the entity is changed.
        """
        if not self.initialized:
            return

        entity = str(entity) if entity is not None else None
        old_entity = str(old_entity) if old_entity is not None else None

        if old_entity == entity:
            return

        if old_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, self.settings.get_uuid())

        if entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.settings.get_uuid(), self._entity_updated)

            self._load_attributes()
            service_parameters_helper.load_service_parameters(self)

        self._reload()

    def _on_change_service(self, _, __, ___) -> None:
        """
        Execute when the service is changed.
        """
        if not self.initialized:
            return

        self.settings.clear_service_parameters()

        service_parameters_helper.load_service_parameters(self)

        self._reload()

    def _entity_updated(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        if not self.initialized:
            return

        # different entities have different attributes -> reload
        self._load_attributes()

        show_icon = self.settings.get_show_icon()
        show_text = self.settings.get_show_text()

        if not show_icon and not show_text:
            self.set_media()
            self._clear_labels()
            return

        entity = self.settings.get_entity()

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
        domain = self.settings.get_domain()

        domains = sorted(self.plugin_base.backend.get_domains())

        if not domain in domains:
            domains.append(domain)

        self.entity_domain_combo.populate(domains, domain, trigger_callback=False)

    def _load_entities(self):
        """
        Load entities from Home Assistant.
        """
        entity = self.settings.get_entity()

        entities = sorted(
            self.plugin_base.backend.get_entities(
                str(self.entity_domain_combo.get_selected_item())))

        if not entity in entities:
            entities.append(entity)

        self.entity_entity_combo.populate(entities, entity, trigger_callback=False)

    def _load_services(self):
        """
        Load services from Home Assistant.
        """
        service = self.settings.get_service()

        services = self.plugin_base.backend.get_services(
            str(self.entity_domain_combo.get_selected_item()))

        self.service_service_combo.populate(services, service, update_settings=True, trigger_callback=False)
        service_parameters_helper.load_service_parameters(self)

    def _load_attributes(self):
        """
        Load entity attributes from Home Assistant.
        """
        attribute = self.settings.get_text_attribute()

        ha_entity = self.plugin_base.backend.get_entity(self.settings.get_entity())

        attribute_model = [const.STATE]
        attribute_model.extend(list(ha_entity.get(const.ATTRIBUTES, {}).keys()))

        if not attribute in attribute_model:
            attribute_model.append(attribute)

        if Counter(attribute_model) != Counter(self._get_current_attributes()):
            self.text_attribute_combo.populate(attribute_model, attribute, trigger_callback=False)

    def _load_custom_icons(self):
        self.icon_custom_icon_expander.clear_rows()

        attributes = self._get_current_attributes()

        state = self.plugin_base.backend.get_entity(self.settings.get_entity())

        for index, customization in enumerate(self.settings.get_icon_customizations()):
            row = CustomizationIconRow(self.lm, customization,
                                       len(self.settings.get_icon_customizations()), index,
                                       attributes, state, self.settings)

            row.edit_button.connect(const.CONNECT_CLICKED, self._on_add_customization,
                                    const.CUSTOMIZATION_TYPE_ICON, self._add_custom_icon,
                                    index)

            row.delete_button.connect(const.CONNECT_CLICKED, self._on_delete_customization,
                                      const.CUSTOMIZATION_TYPE_ICON, index)

            row.up_button.connect(const.CONNECT_CLICKED, self._on_move_up,
                                  const.CUSTOMIZATION_TYPE_ICON, index)

            row.down_button.connect(const.CONNECT_CLICKED, self._on_move_down,
                                    const.CUSTOMIZATION_TYPE_ICON, index)

            self.icon_custom_icon_expander.add_row(row)

    def _load_custom_text(self):
        self.text_custom_text_expander.clear_rows()

        attributes = self._get_current_attributes()

        state = self.plugin_base.backend.get_entity(self.settings.get_entity())

        for index, customization in enumerate(self.settings.get_text_customizations()):
            row = CustomizationTextRow(self.lm, customization, len(self.settings.get_text_customizations()), index, attributes, state, self.settings)

            row.edit_button.connect(const.CONNECT_CLICKED, self._on_add_customization, const.CUSTOMIZATION_TYPE_TEXT, self._add_custom_text, index)

            row.delete_button.connect(const.CONNECT_CLICKED, self._on_delete_customization, const.CUSTOMIZATION_TYPE_TEXT, index)

            row.up_button.connect(const.CONNECT_CLICKED, self._on_move_up, const.CUSTOMIZATION_TYPE_TEXT, index)

            row.down_button.connect(const.CONNECT_CLICKED, self._on_move_down, const.CUSTOMIZATION_TYPE_TEXT, index)

            self.text_custom_text_expander.add_row(row)

    def _on_add_customization(self, _, customization_type: str, callback,
                              index: int = -1):
        attributes = self._get_current_attributes()

        current = None

        if index > -1:
            if customization_type == const.CUSTOMIZATION_TYPE_ICON:
                current = self.settings.get_icon_customizations()[index]
            else:
                current = self.settings.get_text_customizations()[index]

        if customization_type == const.CUSTOMIZATION_TYPE_ICON:
            window = CustomizationIconWindow(self.lm, attributes, callback, current=current,
                                             index=index)
        elif customization_type == const.CUSTOMIZATION_TYPE_TEXT:
            window = CustomizationTextWindow(self.lm, attributes, callback, current=current,
                                             index=index)
        else:
            raise ValueError(f"Unknown customization type: {customization_type}")

        window.show()

    def _on_delete_customization(self, _, customization_type: str, index: int):
        if customization_type == const.CUSTOMIZATION_TYPE_ICON:
            self.settings.remove_icon_customization(index)
        else:
            self.settings.remove_text_customization(index)

        self._load_custom_icons()
        self._load_custom_text()

        self._entity_updated()

    def _on_move_up(self, _, customization_type: str, index: int):
        if customization_type == const.CUSTOMIZATION_TYPE_ICON:
            self.settings.move_icon_customization(index, -1)
        else:
            self.settings.move_text_customization(index, -1)

        self._load_custom_icons()
        self._load_custom_text()

        self._entity_updated()

    def _on_move_down(self, _, customization_type: str, index: int):
        if customization_type == const.CUSTOMIZATION_TYPE_ICON:
            self.settings.move_icon_customization(index, 1)
        else:
            self.settings.move_text_customization(index, 1)

        self._load_custom_icons()
        self._load_custom_text()

        self._entity_updated()

    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        if not self.initialized:
            return

        # Entity section
        domain = self.settings.get_domain()
        is_domain_set = bool(domain)
        self.entity_entity_combo.set_sensitive(
            is_domain_set and self.entity_entity_combo.get_item_amount() > 1)

        # Service section
        entity = self.settings.get_entity()
        is_entity_set = bool(entity)

        if not is_domain_set:
            self.service_call_service.widget.set_sensitive(False)
            self.service_call_service.set_enable_expansion(False)
            self.service_call_service.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_DOMAIN))
        elif not is_entity_set:
            self.service_call_service.widget.set_sensitive(False)
            self.service_call_service.set_enable_expansion(False)
            self.service_call_service.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_ENTITY))
        elif self.service_service_combo.get_item_amount() == 0:
            self.service_call_service.widget.set_sensitive(False)
            self.service_call_service.set_enable_expansion(False)
            self.service_call_service.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_SERVICES))
        else:
            self.service_call_service.widget.set_sensitive(True)
            self.service_call_service.widget.set_subtitle(const.EMPTY_STRING)

        if len(self.service_parameters.widget.get_rows()) > 0:
            self.service_parameters.widget.set_sensitive(True)
            self.service_parameters.widget.set_subtitle(const.EMPTY_STRING)
        else:
            self.service_parameters.widget.set_sensitive(False)
            self.service_parameters.set_expanded(False)
            self.service_parameters.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_PARAMETERS))

        # Icon section
        if not is_entity_set:
            self.icon_show_icon.widget.set_sensitive(False)
            self.icon_show_icon.set_enable_expansion(False)
            self.icon_show_icon.widget.set_subtitle(self.lm.get(const.LABEL_ICON_NO_ENTITY))
        else:
            self.icon_show_icon.widget.set_sensitive(True)
            self.icon_show_icon.widget.set_subtitle(const.EMPTY_STRING)
            self.icon_custom_icon_expander.set_expanded(
                len(self.settings.get_icon_customizations()) > 0)

        # Text section
        if not is_entity_set:
            self.text_show_text.widget.set_sensitive(False)
            self.text_show_text.set_enable_expansion(False)
            self.text_show_text.widget.set_subtitle(self.lm.get(const.LABEL_TEXT_NO_ENTITY))
        else:
            self.text_show_text.widget.set_sensitive(True)
            self.text_show_text.widget.set_subtitle(const.EMPTY_STRING)

            ha_entity = self.plugin_base.backend.get_entity(
                self.settings.get_entity())

            self.text_attribute_combo.set_sensitive(self.text_attribute_combo.get_item_amount() > 1)
            self.text_position_combo.set_sensitive(True)

            has_unit = bool(
                ha_entity.get(const.ATTRIBUTES, {}).get(const.ATTRIBUTE_UNIT_OF_MEASUREMENT, False))

            if has_unit:
                self.text_show_unit.widget.set_sensitive(True)
                self.text_unit_line_break.widget.set_sensitive(True)
            else:
                self.text_show_unit.set_active(False)
                self.text_show_unit.widget.set_sensitive(False)
                self.text_unit_line_break.set_active(False)
                self.text_unit_line_break.widget.set_sensitive(False)

            if not self.text_show_unit.get_active():
                self.text_unit_line_break.set_active(False)
                self.text_unit_line_break.widget.set_sensitive(False)

            self.text_custom_text_expander.set_expanded(
                len(self.settings.get_text_customizations()) > 0)

    def _get_current_attributes(self) -> List[str]:
        """
        Gets the list of attributes set on the Combo as strings.
        :return: the list of attributes set on the Combo as strings
        """
        return [str(self.text_attribute_combo.get_item_at(i)) for i in range(self.text_attribute_combo.get_item_amount())]
