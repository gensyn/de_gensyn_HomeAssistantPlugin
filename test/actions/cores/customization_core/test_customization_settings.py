import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

class TestCustomizationSettings(unittest.TestCase):
    def setUp(self):
        # Patch customization_const.SETTING_CUSTOMIZATIONS
        self.const_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_settings.customization_const")
        self.mock_const = self.const_patch.start()
        self.mock_const.SETTING_CUSTOMIZATIONS = "customizations"

        # Patch BaseSettings
        self.basesettings_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_settings.BaseSettings")
        self.MockBaseSettings = self.basesettings_patch.start()

        # Patch Customization
        self.customization_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_settings.Customization")
        self.MockCustomization = self.customization_patch.start()

        # Import after patching
        from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_settings
        self.customization_settings = customization_settings

        # Setup mocks for dependencies
        self.mock_action = MagicMock()
        self.customization_name = "my_cust"
        self.mock_implementation = MagicMock()
        self.mock_implementation.from_dict.side_effect = lambda d: f"Customization({d})"

        # Example settings dict
        self.example_settings = {
            self.customization_name: {
                self.mock_const.SETTING_CUSTOMIZATIONS: [
                    {"a": 1}, {"b": 2}, {"c": 3}
                ]
            }
        }

        # Patch _settings and _action in instance
        self.settings = self.customization_settings.CustomizationSettings(
            self.mock_action, self.customization_name, self.mock_implementation
        )
        self.settings._action = self.mock_action
        self.settings._action.get_settings.return_value = self.example_settings

    def tearDown(self):
        self.const_patch.stop()
        self.basesettings_patch.stop()
        self.customization_patch.stop()

    def test_get_customizations(self):
        result = self.settings.get_customizations()
        expected = [
            "Customization({'a': 1})",
            "Customization({'b': 2})",
            "Customization({'c': 3})"
        ]
        self.assertEqual(result, expected)
        self.mock_implementation.from_dict.assert_any_call({"a": 1})
        self.mock_implementation.from_dict.assert_any_call({"b": 2})
        self.mock_implementation.from_dict.assert_any_call({"c": 3})

    def test_move_customization(self):
        self.settings._action.set_settings.reset_mock()
        expected = deepcopy(self.example_settings)
        entry = expected[self.customization_name][self.mock_const.SETTING_CUSTOMIZATIONS].pop(0)
        expected[self.customization_name][self.mock_const.SETTING_CUSTOMIZATIONS].insert(2, entry)

        self.settings.move_customization(0, 2)
        self.assertEqual(expected, self.settings._action.get_settings())
        self.settings._action.set_settings.assert_called_once_with(expected)

    def test_remove_customization(self):
        self.settings._action.set_settings.reset_mock()
        # Remove at index 1 ('b':2)
        self.settings.remove_customization(1)
        self.assertEqual(
            self.settings._action.get_settings()[self.customization_name][self.mock_const.SETTING_CUSTOMIZATIONS], [{"a": 1}, {"c": 3}]
        )
        self.settings._action.set_settings.assert_called_once_with(self.settings._action.get_settings())

    def test_replace_customization(self):
        self.settings._action.set_settings.reset_mock()
        # Replace index 0 with a mock customization
        mock_cust = MagicMock()
        mock_cust.export.return_value = {"foo": "bar"}
        self.settings.replace_customization(0, mock_cust)
        self.assertEqual(
            self.settings._action.get_settings()[self.customization_name][self.mock_const.SETTING_CUSTOMIZATIONS][0],
            {"foo": "bar"}
        )
        self.settings._action.set_settings.assert_called_once_with(self.settings._action.get_settings())
        mock_cust.export.assert_called_once()

    def test_add_customization(self):
        self.settings._action.set_settings.reset_mock()
        expected = deepcopy(self.example_settings)
        expected[self.customization_name][self.mock_const.SETTING_CUSTOMIZATIONS].append({"baz": 42})
        mock_cust = MagicMock()
        mock_cust.export.return_value = {"baz": 42}
        self.settings.add_customization(mock_cust)
        self.assertIn(
            {"baz": 42},
            self.example_settings[self.customization_name][self.mock_const.SETTING_CUSTOMIZATIONS]
        )
        self.settings._action.set_settings.assert_called_once_with(expected)
        mock_cust.export.assert_called_once()