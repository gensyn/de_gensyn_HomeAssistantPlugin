"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import json
from json import JSONDecodeError

from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.GenerativeUI.ExpanderRow import ExpanderRow
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.EventAssigner import EventAssigner
from de_gensyn_HomeAssistantPlugin.actions.perform_action import const
from de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters import action_parameters_helper
from de_gensyn_HomeAssistantPlugin.actions.perform_action.settings.action_settings import ActionSettings
from de_gensyn_HomeAssistantPlugin.actions.home_assistant_action_core import HomeAssistantActionCore


class PerformAction(HomeAssistantActionCore):
    """Action to be loaded by StreamController."""

    def __init__(self, *args, **kwargs):
        super().__init__(track_entity=False, *args, **kwargs)

    def on_ready(self) -> None:
        """Set up action when StreamController has finished loading."""
        self.settings: ActionSettings = ActionSettings(self)

        super().on_ready()

        if not self.plugin_base.backend.is_connected():
            return

        super().on_ready()
        self._load_actions()
        self.initialized = True
        self._reload()

    def _perform_action(self, _) -> None:
        """Call the action stated in the settings."""
        domain = self.settings.get_domain()
        action = self.settings.get_action()
        if not domain or not action:
            return

        parameters = {}
        for parameter, value in self.settings.get_parameters().items():
            try:
                # try to create a dict or list from the value
                value = json.loads(value)
            except (JSONDecodeError, TypeError):
                # if it doesn't work just keep it as is
                pass
            parameters[parameter] = value

        entity = self.settings.get_entity()

        self.plugin_base.backend.perform_action(domain, action, entity, parameters)

    def _create_event_assigner(self) -> None:
        self.add_event_assigner(EventAssigner(
            id=const.ACTION_ID,
            ui_label=const.ACTION_NAME,
            default_events=[Input.Key.Events.DOWN],
            callback=self._perform_action
        ))

    def get_config_rows(self) -> list:
        """Get the rows to be displayed in the UI."""
        return [self.domain_combo.widget, self.action_combo.widget, self.entity_combo.widget,
                self.parameters_expander.widget]

    def _create_ui_elements(self) -> None:
        """Get all action rows."""
        super()._create_ui_elements()
        self.action_combo: ComboRow = ComboRow(
            self, const.SETTING_ACTION_ACTION, const.EMPTY_STRING, [],
            const.LABEL_SERVICE_SERVICE, enable_search=True,
            on_change=self._on_change_action, can_reset=False,
            complex_var_name=True
        )

        self.parameters_expander: ExpanderRow = ExpanderRow(
            self, const.EMPTY_STRING, False,
            title=const.LABEL_SERVICE_PARAMETERS, can_reset=False,
            auto_add=False
        )

    def _on_change_domain(self, _, domain, old_domain):
        """Execute when the domain is changed."""
        if not self.initialized:
            return
        super()._on_change_domain(_, domain, old_domain)

        domain = str(domain) if domain is not None else None
        if domain:
            self._load_actions()

        self._set_enabled_disabled()

    def _on_change_entity(self, _, entity, old_entity):
        """Execute when the entity is changed."""
        if not self.initialized:
            return

        entity = str(entity) if entity is not None else None
        old_entity = str(old_entity) if old_entity is not None else None

        if old_entity == entity:
            return

        super()._on_change_entity(_, entity, old_entity)

        if entity:
            action_parameters_helper.load_parameters(self)

        self._reload()

    def _on_change_action(self, _, __, ___) -> None:
        """Execute when the action is changed."""
        if not self.initialized:
            return

        self.settings.clear_parameters()
        action_parameters_helper.load_parameters(self)
        self._reload()

    def _load_actions(self) -> None:
        """
        Load actions from Home Assistant.
        """
        action = self.settings.get_action()
        actions_dict = self.plugin_base.backend.get_actions(
            str(self.domain_combo.get_selected_item())
        )
        actions = list(actions_dict.keys())
        if action not in actions:
            actions.append(action)
        self.action_combo.populate(actions, action, update_settings=True, trigger_callback=False)
        action_parameters_helper.load_parameters(self)

    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        if not self.initialized:
            return

        domain = self.settings.get_domain()
        is_domain_set = bool(domain)

        if not is_domain_set:
            self.action_combo.widget.set_sensitive(False)
            self.action_combo.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_DOMAIN))
            self.parameters_expander.widget.set_sensitive(False)
            self.parameters_expander.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_DOMAIN))
        elif self.action_combo.get_item_amount() == 0:
            self.action_combo.widget.set_sensitive(False)
            self.action_combo.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_ACTIONS))
            self.parameters_expander.widget.set_sensitive(False)
            self.parameters_expander.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_ACTIONS))
        else:
            self.action_combo.widget.set_sensitive(True)
            self.action_combo.widget.set_subtitle(const.EMPTY_STRING)

            if len(self.parameters_expander.widget.get_rows()) == 0:
                self.parameters_expander.widget.set_sensitive(False)
                self.parameters_expander.set_expanded(False)
                self.parameters_expander.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_PARAMETERS))
            else:
                self.parameters_expander.widget.set_sensitive(True)
                self.parameters_expander.set_expanded(True)
                self.parameters_expander.widget.set_subtitle(const.EMPTY_STRING)

            action = self.settings.get_action()
            actions = self.plugin_base.backend.get_actions(
                str(self.domain_combo.get_selected_item())
            )
            has_target = bool(actions.get(action, {}).get(const.TARGET))
            self.entity_combo.widget.set_sensitive(has_target and self.entity_combo.get_item_amount() > 1)

    def _get_domains(self):
        """This class needs all domains that provide actions in Home Assistant."""
        return self.plugin_base.backend.get_domains_for_actions()
