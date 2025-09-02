import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action import ShowIcon
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_row import IconRow
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_window import IconWindow

class TestShowIcon(unittest.TestCase):
    def setUp(self):
        # Patch dependencies and core attributes
        self.mock_plugin_base = MagicMock()
        self.mock_plugin_base.backend.is_connected.return_value = True
        self.mock_plugin_base.backend.get_entity.return_value = {"state": "on"}
        self.mock_plugin_base.backend.get_domains_for_entities.return_value = ["light", "sensor"]

        # Patch ShowIconSettings, IconWindow, IconCustomization, IconRow
        patcher_settings = patch(
            "de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.ShowIconSettings",
            autospec=True
        )
        self.MockShowIconSettings = patcher_settings.start()
        self.addCleanup(patcher_settings.stop)

        patcher_icon_helper = patch(
            "de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.icon_helper.get_icon",
            return_value=("mdi:lightbulb", 24)
        )
        self.mock_get_icon = patcher_icon_helper.start()
        self.addCleanup(patcher_icon_helper.stop)

        patcher_icon_const = patch(
            "de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.icon_const"
        )
        self.mock_icon_const = patcher_icon_const.start()
        self.addCleanup(patcher_icon_const.stop)

        # Patch EntryRow, ColorButtonRow, ScaleRow
        patcher_entry_row = patch("de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.EntryRow")
        self.MockEntryRow = patcher_entry_row.start()
        self.addCleanup(patcher_entry_row.stop)

        patcher_color_button_row = patch("de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.ColorButtonRow")
        self.MockColorButtonRow = patcher_color_button_row.start()
        self.addCleanup(patcher_color_button_row.stop)

        patcher_scale_row = patch("de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.ScaleRow")
        self.MockScaleRow = patcher_scale_row.start()
        self.addCleanup(patcher_scale_row.stop)

        # Patch CustomizationCore methods
        patcher_super_init = patch("de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.CustomizationCore.__init__")
        self.MockSuperInit = patcher_super_init.start()
        self.addCleanup(patcher_super_init.stop)

        self.icon_row = MagicMock()
        self.icon_window = MagicMock()
        self.icon_customization = MagicMock()

        # Set up instance
        self.instance = ShowIcon("arg1", "arg2", test_kw="testval")
        self.instance.plugin_base = self.mock_plugin_base
        self.instance.lm = MagicMock()
        self.instance.domain_combo = MagicMock()
        self.instance.domain_combo.widget = MagicMock()
        self.instance.entity_combo = MagicMock()
        self.instance.entity_combo.widget = MagicMock()
        self.instance.customization_expander = MagicMock()
        self.instance.customization_expander.widget = MagicMock()
        self.instance.set_media = MagicMock()
        self.instance._reload = MagicMock()
        self.instance._load_customizations = MagicMock()
        self.instance.initialized = False

        # Settings mock
        self.mock_settings = MagicMock()
        self.mock_settings.get_domain.return_value = "light"
        self.mock_settings.get_entity.return_value = "light.bedroom"
        self.instance.settings = self.mock_settings

        # Rows
        self.instance.icon = MagicMock()
        self.instance.icon.widget = MagicMock()
        self.instance.color = MagicMock()
        self.instance.color.widget = MagicMock()
        self.instance.scale = MagicMock()
        self.instance.scale.widget = MagicMock()
        self.instance.opacity = MagicMock()
        self.instance.opacity.widget = MagicMock()

    def test_init(self):
        self.MockSuperInit.assert_called_once_with(
            "arg1", "arg2",
            window_implementation=IconWindow,
            customization_implementation=IconCustomization,
            row_implementation=IconRow,
            track_entity=True,
            settings_implementation=self.MockShowIconSettings,
            test_kw="testval"
        )

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core.log.info')
    def test_on_ready_connected(self, _):
        self.mock_plugin_base.backend.is_connected.return_value = True
        # Patch _reload so we can check it's called
        self.instance._reload = MagicMock()
        # Patch ShowIconSettings
        self.instance.track_entity = True
        self.instance.settings_implementation = MagicMock()
        # Actually call the real method
        self.instance.on_ready.__func__(self.instance)
        self.instance._reload.assert_called()
        self.assertTrue(self.instance.initialized)

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core.log.info')
    def test_on_ready_not_connected(self, _):
        self.mock_plugin_base.backend.is_connected.return_value = False
        self.instance.refresh = MagicMock()
        self.MockShowIconSettings.return_value = self.mock_settings
        self.instance.track_entity = True
        self.instance.settings_implementation = MagicMock()
        self.instance.on_ready.__func__(self.instance)
        self.instance.refresh.assert_called()
        self.assertFalse(self.instance.initialized)

    def test_get_config_rows(self):
        rows = self.instance.get_config_rows()
        self.assertIn(self.instance.domain_combo.widget, rows)
        self.assertIn(self.instance.entity_combo.widget, rows)
        self.assertIn(self.instance.icon.widget, rows)
        self.assertIn(self.instance.color.widget, rows)
        self.assertIn(self.instance.scale.widget, rows)
        self.assertIn(self.instance.opacity.widget, rows)
        self.assertIn(self.instance.customization_expander.widget, rows)
        self.assertEqual(len(rows), 7)

    def test_create_ui_elements(self):
        self.instance._create_ui_elements()
        self.MockEntryRow.assert_called()
        self.MockColorButtonRow.assert_called()
        self.MockScaleRow.assert_called()

    def test_set_enabled_disabled_not_initialized(self):
        self.instance.initialized = False
        # Should early return, so widgets not touched
        self.instance._set_enabled_disabled()
        # No assertion necessary (no-op)

    def test_set_enabled_disabled_no_domain_or_entity(self):
        self.instance.initialized = True
        self.mock_settings.get_domain.return_value = ""
        self.mock_settings.get_entity.return_value = ""
        self.instance.lm.get.return_value = "NO_ENTITY"
        self.instance._set_enabled_disabled()
        self.instance.icon.widget.set_sensitive.assert_called_with(False)
        self.instance.color.widget.set_sensitive.assert_called_with(False)
        self.instance.color.widget.set_subtitle.assert_called_with("NO_ENTITY")
        self.instance.scale.widget.set_sensitive.assert_called_with(False)
        self.instance.scale.widget.set_subtitle.assert_called_with("NO_ENTITY")
        self.instance.opacity.widget.set_sensitive.assert_called_with(False)
        self.instance.opacity.widget.set_subtitle.assert_called_with("NO_ENTITY")

    def test_set_enabled_disabled_with_domain_and_entity(self):
        self.instance.initialized = True
        self.mock_settings.get_domain.return_value = "light"
        self.mock_settings.get_entity.return_value = "light.bedroom"
        with patch("de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_action.CustomizationCore._set_enabled_disabled"):
            self.instance._set_enabled_disabled()
        self.instance.icon.widget.set_sensitive.assert_called_with(True)
        self.instance.color.widget.set_sensitive.assert_called_with(True)
        self.instance.color.widget.set_subtitle.assert_called_with(self.mock_icon_const.EMPTY_STRING)
        self.instance.scale.widget.set_sensitive.assert_called_with(True)
        self.instance.scale.widget.set_subtitle.assert_called_with(self.mock_icon_const.EMPTY_STRING)
        self.instance.opacity.widget.set_sensitive.assert_called_with(True)
        self.instance.opacity.widget.set_subtitle.assert_called_with(self.mock_icon_const.EMPTY_STRING)

    def test_refresh_not_initialized_not_connected(self):
        self.instance.initialized = False
        self.mock_plugin_base.backend.is_connected.return_value = False
        self.mock_get_icon.return_value = ("mdi:lightbulb", 24)
        self.instance.set_media = MagicMock()
        self.instance.refresh({"state": "on"})
        self.instance.set_media.assert_called_with(media_path="mdi:lightbulb", size=24)

    def test_refresh_not_initialized_connected(self):
        self.instance.initialized = False
        self.mock_plugin_base.backend.is_connected.return_value = True
        self.instance.set_media = MagicMock()
        self.instance.refresh({"state": "on"})
        # Should not call set_media (early return)
        self.instance.set_media.assert_not_called()

    def test_refresh_with_state_none(self):
        self.instance.initialized = True
        self.mock_settings.get_entity.return_value = "light.bedroom"
        self.mock_plugin_base.backend.get_entity.return_value = None
        self.instance.set_media = MagicMock()
        self.instance.refresh(None)
        self.instance.set_media.assert_called_with()

    def test_refresh_with_state(self):
        self.instance.initialized = True
        self.mock_plugin_base.backend.is_connected.return_value = True
        self.mock_plugin_base.backend.get_entity.return_value = {"state": "on"}
        self.mock_settings.get_entity.return_value = "light.bedroom"
        self.instance.set_media = MagicMock()
        self.instance._load_customizations = MagicMock()
        self.instance._set_enabled_disabled = MagicMock()
        self.instance.refresh({"state": "on"})
        self.instance.set_media.assert_called_with(media_path="mdi:lightbulb", size=24)
        self.instance._load_customizations.assert_called()
        self.instance._set_enabled_disabled.assert_called()

    def test__get_domains(self):
        self.mock_plugin_base.backend.get_domains_for_entities.return_value = ["light", "sensor"]
        domains = self.instance._get_domains()
        self.assertEqual(domains, ["light", "sensor"])

if __name__ == "__main__":
    unittest.main()