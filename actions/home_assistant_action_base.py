"""
The module for the Home Assistant action that is loaded in StreamController.
"""

from typing import List, Optional

import gi

gi.require_version("Adw", "1")
from gi.repository.Gtk import Widget
from gi.repository.Adw import PreferencesGroup

from GtkHelper.GenerativeUI.ComboRow import ComboRow
from de_gensyn_HomeAssistantPlugin.actions import const
from de_gensyn_HomeAssistantPlugin.actions.settings.settings import Settings
from src.backend.PluginManager.ActionBase import ActionBase


class HomeAssistantActionBase(ActionBase):
    """Action base for all Home Assistant Actions."""

    def __init__(self, track_entity: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings: Optional[Settings] = None
        self.initialized = False
        self.lm = self.plugin_base.locale_manager
        self.has_configuration = True
        self.track_entity = track_entity
        self._init_entity_group()


    def on_ready(self) -> None:
        """Set up action when StreamController has finished loading."""

        if not self.plugin_base.backend.is_connected():
            self.plugin_base.backend.register_action(self.on_ready)

        entity = self.settings.get_entity()
        if entity and self.track_entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.settings.get_uuid(), self._entity_updated)

        self._load_domains()
        self._load_entities()

    def on_remove(self) -> None:
        """Clean up after action was removed."""
        self.plugin_base.backend.remove_action(self.on_ready)

        if self.track_entity:
            self.plugin_base.backend.remove_tracked_entity(
                self.settings.get_entity(),
                self.settings.get_uuid()
            )
        self._entity_updated()

    def get_config_rows(self) -> List[PreferencesGroup]:
        """Get the rows to be displayed in the UI."""
        return [self._entity_group]

    def _init_entity_group(self) -> None:
        """Get all entity rows."""
        self.entity_domain_combo: ComboRow = ComboRow(
            self, const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING, [],
            const.LABEL_ENTITY_DOMAIN, enable_search=True,
            on_change=self._on_change_domain, can_reset=False,
            complex_var_name=True
        )

        self.entity_entity_combo: ComboRow = ComboRow(
            self, const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING, [],
            const.LABEL_ENTITY_ENTITY, enable_search=True,
            on_change=self._on_change_entity, can_reset=False,
            complex_var_name=True
        )

        self._entity_group = self._create_group(
            const.LABEL_SETTINGS_ENTITY,
            [self.entity_domain_combo.widget, self.entity_entity_combo.widget]
        )

    def _create_group(self, title_const: str, widgets: List[Widget]) -> PreferencesGroup:
        group = PreferencesGroup()
        group.set_title(self.lm.get(title_const))
        group.set_margin_top(20)
        for widget in widgets:
            group.add(widget)
        return group

    def _reload(self, *_):
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
                self.plugin_base.backend.remove_tracked_entity(entity, self.settings.get_uuid())
            self.settings.reset(domain)
            self.entity_entity_combo.remove_all_items()

        if domain:
            self._load_entities()

        self._set_enabled_disabled()

    def _on_change_entity(self, _, entity, old_entity):
        """Execute when the entity is changed."""
        entity = str(entity) if entity is not None else None
        old_entity = str(old_entity) if old_entity is not None else None

        if old_entity and self.track_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, self.settings.get_uuid())

        if entity and self.track_entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.settings.get_uuid(), self._entity_updated)

        self._set_enabled_disabled()

    def _entity_updated(self, state: dict = None) -> None:
        """Executed when an entity is updated to reflect the changes on the key."""
        pass

    def _load_domains(self) -> None:
        """
        Load domains from Home Assistant.
        """
        domain = self.settings.get_domain()
        domains = sorted(self.plugin_base.backend.get_domains())
        if domain not in domains:
            domains.append(domain)
        self.entity_domain_combo.populate(domains, domain, trigger_callback=False)

    def _load_entities(self) -> None:
        """
        Load entities from Home Assistant.
        """
        entity = self.settings.get_entity()
        entities = sorted(
            self.plugin_base.backend.get_entities(
                str(self.entity_domain_combo.get_selected_item())
            )
        )
        if entity not in entities:
            entities.append(entity)
        self.entity_entity_combo.populate(entities, entity, trigger_callback=False)

    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        if not self.initialized:
            return

        self.settings.load()

        # Entity section
        domain = self.settings.get_domain()
        is_domain_set = bool(domain)
        self.entity_entity_combo.set_sensitive(
            is_domain_set and self.entity_entity_combo.get_item_amount() > 1
        )
