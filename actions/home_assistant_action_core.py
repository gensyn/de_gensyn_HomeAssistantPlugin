"""The module for the Home Assistant action that is loaded in StreamController."""

from typing import List, Optional

import gi

from src.backend.PluginManager.ActionCore import ActionCore

gi.require_version("Adw", "1")
from gi.repository.Adw import PreferencesGroup

from GtkHelper.GenerativeUI.ComboRow import ComboRow
from de_gensyn_HomeAssistantPlugin.actions import const
from de_gensyn_HomeAssistantPlugin.actions.settings.settings import Settings


class HomeAssistantActionCore(ActionCore):
    """Action core for all Home Assistant Actions."""

    def __init__(self, track_entity: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings: Optional[Settings] = None
        self.initialized = False
        self.lm = self.plugin_base.locale_manager
        self.has_configuration = True
        self.track_entity = track_entity
        self._create_ui_elements()
        self._create_event_assigner()

    def on_ready(self) -> None:
        """Set up action when StreamController has finished loading."""
        self.plugin_base.backend.add_action_ready_callback(self.on_ready)

        entity = self.settings.get_entity()
        if entity and self.track_entity:
            self.plugin_base.backend.add_tracked_entity(entity, self._entity_updated)

        self._load_domains()
        self._load_entities()

    def on_remove(self) -> None:
        """Clean up after action was removed."""
        self.plugin_base.backend.remove_action_ready_callback(self.on_ready)

        if self.track_entity:
            self.plugin_base.backend.remove_tracked_entity(
                self.settings.get_entity(),
                self._entity_updated
            )
        self._entity_updated()

    def get_config_rows(self) -> List[PreferencesGroup]:
        """Get the rows to be displayed in the UI."""
        raise NotImplementedError("Must be implemented by subclasses.")

    def _create_ui_elements(self) -> None:
        """Get all entity rows."""
        self.domain_combo: ComboRow = ComboRow(
            self, const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING, [],
            const.LABEL_ENTITY_DOMAIN, enable_search=True,
            on_change=self._on_change_domain, can_reset=False,
            complex_var_name=True
        )

        self.entity_combo: ComboRow = ComboRow(
            self, const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING, [],
            const.LABEL_ENTITY_ENTITY, enable_search=True,
            on_change=self._on_change_entity, can_reset=False,
            complex_var_name=True
        )

    def _reload(self, *_):
        """Reload the action."""
        self.settings.load()
        self._set_enabled_disabled()
        self._entity_updated()

    def _on_change_domain(self, _, domain, old_domain):
        """Execute when the domain is changed."""
        domain = str(domain) if domain is not None else None
        old_domain = str(old_domain) if old_domain is not None else None

        if old_domain != domain:
            entity = self.settings.get_entity()
            if entity and self.track_entity:
                self.plugin_base.backend.remove_tracked_entity(entity, self._entity_updated)
            self.settings.reset(domain)
            self.entity_combo.remove_all_items()

        if domain:
            self._load_entities()

        self._set_enabled_disabled()

    def _on_change_entity(self, _, entity, old_entity):
        """Execute when the entity is changed."""
        entity = str(entity) if entity is not None else None
        old_entity = str(old_entity) if old_entity is not None else None

        if old_entity and self.track_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, self._entity_updated)

        if entity and self.track_entity:
            self.plugin_base.backend.add_tracked_entity(entity, self._entity_updated)

        self._set_enabled_disabled()

    def _entity_updated(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        This does not need to do anything by default, but can be overridden by subclasses.
        :param state: The state of the entity, if available.
        """
        pass

    def _create_event_assigner(self) -> None:
        """
        Create the events that can be triggered in this action.
        This does not need to do anything by default, but can be overridden by subclasses.
        """
        pass

    def _load_domains(self) -> None:
        """Load domains from Home Assistant."""
        domain = self.settings.get_domain()
        domains = sorted(self._get_domains())
        if domain not in domains:
            domains.append(domain)
        self.domain_combo.populate(domains, domain, trigger_callback=False)

    def _load_entities(self) -> None:
        """Load entities from Home Assistant."""
        entity = self.settings.get_entity()
        entities = sorted(
            self.plugin_base.backend.get_entities(
                str(self.domain_combo.get_selected_item())
            )
        )
        if entity not in entities:
            entities.append(entity)
        self.entity_combo.populate(entities, entity, trigger_callback=False)

    def _set_enabled_disabled(self) -> None:
        """Set the active/inactive state for all rows."""
        if not self.initialized:
            return

        self.settings.load()

        domain = self.settings.get_domain()
        is_domain_set = bool(domain)
        self.entity_combo.set_sensitive(
            is_domain_set and self.entity_combo.get_item_amount() > 1
        )

    def _get_domains(self) -> List[str]:
        """Get the domains available in Home Assistant."""
        raise NotImplementedError("Must be implemented by subclasses.")

    def get_generative_ui(self):
        return []
