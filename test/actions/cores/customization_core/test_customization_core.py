import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_core import CustomizationCore


def _mock_base_const():
    m = MagicMock()
    m.CONNECT_CLICKED = "clicked"
    m.EMPTY_STRING = ""
    m.LABEL_CUSTOMIZATION = "Customization"
    m.LABEL_NO_ENTITY = "No Entity"
    return m


def _mock_customization_const():
    m = MagicMock()
    m.STATE = "state"
    m.ATTRIBUTES = "attributes"
    return m


def _mock_settings():
    mock = MagicMock()
    mock.get_customizations.return_value = []
    mock.get_domain.return_value = "domain"
    mock.get_entity.return_value = "entity"
    mock.remove_customization = MagicMock()
    mock.replace_customization = MagicMock()
    mock.add_customization = MagicMock()
    mock.move_customization = MagicMock()
    return mock


def _mock_plugin_base():
    mock = MagicMock()
    mock.backend.get_entity.return_value = {"attributes": {"attr1": "value1", "attr2": "value2"}}
    return mock


def _mock_lm():
    mock = MagicMock()
    mock.get.return_value = "No Entity"
    return mock


def _mock_expander_row():
    expander = MagicMock()
    expander.widget = MagicMock()
    expander.widget.add_suffix = MagicMock()
    expander.widget.set_sensitive = MagicMock()
    expander.widget.set_subtitle = MagicMock()
    expander.widget.set_expanded = MagicMock()
    expander.clear_rows = MagicMock()
    expander.add_row = MagicMock()
    expander.set_expanded = MagicMock()
    return expander


def _mock_row_implementation():
    def row_impl(lm, customization, total, index, attributes, state, settings):
        row = MagicMock()
        row.edit_button = MagicMock()
        row.edit_button.connect = MagicMock()
        row.delete_button = MagicMock()
        row.delete_button.connect = MagicMock()
        row.up_button = MagicMock()
        row.up_button.connect = MagicMock()
        row.down_button = MagicMock()
        row.down_button.connect = MagicMock()
        return row

    return row_impl


class TestCustomizationCore(unittest.TestCase):
    def setUp(self):
        # Patch ExpanderRow to always return a MagicMock
        self.expander_patch = patch(
            "de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_core.ExpanderRow",
            new=lambda *a, **kw: self.mock_expander_row
        )
        self.expander_patch.start()
        # Patch base_const and customization_const
        self.base_const_patch = patch(
            "de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_core.base_const",
            new=_mock_base_const()
        )
        self.customization_const_patch = patch(
            "de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_core.customization_const",
            new=_mock_customization_const()
        )
        self.base_const_patch.start()
        self.customization_const_patch.start()

        self.mock_settings = _mock_settings()
        self.mock_plugin_base = _mock_plugin_base()
        self.mock_lm = _mock_lm()
        self.mock_expander_row = _mock_expander_row()
        self.mock_row_implementation = _mock_row_implementation()

        self.core = CustomizationCore(
            window_implementation=MagicMock(),
            customization_implementation=MagicMock(),
            row_implementation=self.mock_row_implementation,
            track_entity=True
        )
        self.core.lm = self.mock_lm
        self.core.settings = self.mock_settings
        self.core.plugin_base = self.mock_plugin_base
        self.core.initialized = True

    def tearDown(self):
        self.expander_patch.stop()
        self.base_const_patch.stop()
        self.customization_const_patch.stop()

    def test_create_ui_elements(self):
        self.core._create_ui_elements()
        self.core.customization_expander.widget.add_suffix.assert_called()

    def test_on_add_customization(self):
        window_impl = self.core.window_implementation
        window = MagicMock()
        window_impl.return_value = window
        window.show = MagicMock()
        self.core.settings.get_customizations.return_value = ["custom1"]
        self.core._on_add_customization(None, MagicMock(), index=0)
        window.show.assert_called_once()

    def test_add_customization_new(self):
        self.core.settings.get_customizations.return_value = []
        self.core.refresh = MagicMock()
        self.core._add_customization("new_customization", -1)
        self.core.settings.add_customization.assert_called_with("new_customization")
        self.core.refresh.assert_called_once()

    def test_add_customization_edit_duplicate(self):
        self.core.settings.get_customizations.return_value = ["first", "dup"]
        self.core.refresh = MagicMock()
        self.core._load_customizations = MagicMock()
        self.core._add_customization("dup", 0)
        self.core.settings.remove_customization.assert_called_with(0)
        self.core._load_customizations.assert_called_once()
        self.core.refresh.assert_called_once()

    def test_add_customization_edit_replace(self):
        self.core.settings.get_customizations.return_value = ["notdup"]
        self.core.refresh = MagicMock()
        self.core._add_customization("changed", 0)
        self.core.settings.replace_customization.assert_called_with(0, "changed")
        self.core.refresh.assert_called_once()

    def test_on_delete_customization(self):
        self.core.refresh = MagicMock()
        self.core._on_delete_customization(None, 2)
        self.core.settings.remove_customization.assert_called_with(2)
        self.core.refresh.assert_called_once()

    def test_on_move_up_down(self):
        self.core.refresh = MagicMock()
        self.core._on_move_up(None, 1)
        self.core.settings.move_customization.assert_called_with(1, -1)
        self.core.refresh.assert_called_once()
        self.core.refresh.reset_mock()
        self.core._on_move_down(None, 2)
        self.core.settings.move_customization.assert_called_with(2, 1)
        self.core.refresh.assert_called_once()

    def test_set_enabled_disabled_initialization(self):
        self.core.initialized = False
        self.core._set_enabled_disabled()
        # Should return early, nothing to assert

    def test_set_enabled_disabled_no_domain_entity(self):
        self.core.initialized = True
        self.core.settings.get_domain.return_value = ""
        self.core.settings.get_entity.return_value = ""
        self.core._set_enabled_disabled()
        self.core.customization_expander.widget.set_sensitive.assert_called_with(False)
        self.core.customization_expander.widget.set_subtitle.assert_called()
        self.core.customization_expander.widget.set_expanded.assert_called_with(False)

    def test_set_enabled_disabled_with_domain_entity(self):
        self.core.initialized = True
        self.core.settings.get_domain.return_value = "domain"
        self.core.settings.get_entity.return_value = "entity"
        self.core.settings.get_customizations.return_value = ["c1"]
        self.core._set_enabled_disabled()
        self.core.customization_expander.widget.set_sensitive.assert_called_with(True)
        self.core.customization_expander.widget.set_subtitle.assert_called()
        self.core.customization_expander.set_expanded.assert_called()

    def test_get_attributes(self):
        self.core.plugin_base.backend.get_entity.return_value = {"attributes": {"foo": 1, "bar": 2}}
        attrs = self.core._get_attributes()
        self.assertIn("state", attrs)
        self.assertIn("foo", attrs)
        self.assertIn("bar", attrs)

    def test_load_customizations(self):
        self.core.customization_expander.clear_rows = MagicMock()
        self.core.settings.get_customizations.return_value = ["c1", "c2"]
        self.core.plugin_base.backend.get_entity.return_value = {"attributes": {"foo": 1}}
        self.core.customization_expander.add_row = MagicMock()
        self.core._get_attributes = MagicMock(return_value=["state", "foo"])
        self.core._load_customizations()
        self.assertEqual(self.core.customization_expander.add_row.call_count, 2)


if __name__ == "__main__":
    unittest.main()
