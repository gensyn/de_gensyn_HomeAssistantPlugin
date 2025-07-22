"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import json
from json import JSONDecodeError


from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.GenerativeUI.ExpanderRow import ExpanderRow
from de_gensyn_HomeAssistantPlugin.actions.PerformAction import const
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.action_parameters import action_parameters_helper
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.settings.action_settings import ActionSettings
from de_gensyn_HomeAssistantPlugin.actions.home_assistant_action_base import HomeAssistantActionBase


class PerformAction(HomeAssistantActionBase):
    """Action to be loaded by StreamController."""
    def __init__(self, *args, **kwargs):
        super().__init__(track_entity= False, *args, **kwargs)
        self._init_action_group()

    def on_ready(self) -> None:
        """Set up action when StreamController has finished loading."""
        self.settings: ActionSettings = ActionSettings(self)
        super().on_ready()
        self._load_actions()
        self.initialized = True
        self._reload()

    def on_key_down(self) -> None:
        """Call the action stated in the settings."""
        entity = self.settings.get_entity()
        action = self.settings.get_action()
        if not entity or not action:
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

        self.plugin_base.backend.call_action(entity, action, parameters)

    def get_config_rows(self) -> list:
        """Get the rows to be displayed in the UI."""
        rows = super().get_config_rows()
        rows.append(self._action_group)
        return rows

    def _init_action_group(self) -> None:
        """Get all action rows."""
        self.action_combo: ComboRow = ComboRow(
            self, const.SETTING_ACTION_ACTION, const.EMPTY_STRING, [],
            const.LABEL_SERVICE_SERVICE, enable_search=True,
            on_change=self._on_change_action, can_reset=False,
            complex_var_name=True
        )

        self.parameters: ExpanderRow = ExpanderRow(
            self, const.EMPTY_STRING, False,
            title=const.LABEL_SERVICE_PARAMETERS, can_reset=False,
            auto_add=False
        )

        self._action_group = self._create_group(
            const.LABEL_SETTINGS_ACTION, [self.action_combo.widget, self.parameters.widget]
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

        self.settings.clear_action_parameters()
        action_parameters_helper.load_parameters(self)
        self._reload()

    def _load_actions(self) -> None:
        """
        Load actions from Home Assistant.
        """
        action = self.settings.get_action()
        actions = self.plugin_base.backend.get_actions(
            str(self.entity_domain_combo.get_selected_item())
        )
        self.action_combo.populate(actions, action, update_settings=True, trigger_callback=False)
        action_parameters_helper.load_parameters(self)

    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        if not self.initialized:
            return
        super()._set_enabled_disabled()

        # Entity section
        domain = self.settings.get_domain()
        is_domain_set = bool(domain)

        # Action section
        entity = self.settings.get_entity()
        is_entity_set = bool(entity)

        if not is_domain_set:
            self.action_combo.widget.set_sensitive(False)
            self.action_combo.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_DOMAIN))
            self.parameters.widget.set_sensitive(False)
            self.parameters.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_DOMAIN))
        elif not is_entity_set:
            self.action_combo.widget.set_sensitive(False)
            self.action_combo.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_ENTITY))
            self.parameters.widget.set_sensitive(False)
            self.parameters.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_ENTITY))
        elif self.action_combo.get_item_amount() == 0:
            self.action_combo.widget.set_sensitive(False)
            self.action_combo.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_SERVICES))
            self.parameters.widget.set_sensitive(False)
            self.parameters.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_SERVICES))
        else:
            self.action_combo.widget.set_sensitive(True)
            self.action_combo.widget.set_subtitle(const.EMPTY_STRING)

            if len(self.parameters.widget.get_rows()) == 0:
                self.parameters.widget.set_sensitive(False)
                self.parameters.set_expanded(False)
                self.parameters.widget.set_subtitle(self.lm.get(const.LABEL_SERVICE_NO_PARAMETERS))
            else:
                self.parameters.widget.set_sensitive(True)
                self.parameters.widget.set_subtitle(const.EMPTY_STRING)
