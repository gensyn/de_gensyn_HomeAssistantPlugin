import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_settings, icon_const
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_const


class TestShowIconSettings(unittest.TestCase):
    def setUp(self):
        # Setup a fake action object with settings dict
        self.action = MagicMock()
        self.settings_data = {
            icon_const.SETTING_ICON: {
                icon_const.SETTING_ICON: "mdi:thermometer",
                icon_const.SETTING_COLOR: (255, 0, 0, 255),
                icon_const.SETTING_SCALE: 150,
                icon_const.SETTING_OPACITY: 120,
                customization_const.SETTING_CUSTOMIZATIONS: []
            }
        }
        self.action.get_settings.return_value = self.settings_data.copy()
        self.action.set_settings = MagicMock()

    def test_getters(self):
        sis = icon_settings.ShowIconSettings(self.action)
        self.assertEqual(sis.get_icon(), "mdi:thermometer")
        self.assertEqual(sis.get_color(), (255, 0, 0, 255))
        self.assertEqual(sis.get_scale(), 150)
        self.assertEqual(sis.get_opacity(), 120)

    def test_default_settings_initialization(self):
        # Remove icon settings to trigger default initialization
        self.action.get_settings.return_value = {}
        sis = icon_settings.ShowIconSettings(self.action)
        # Should set defaults as per DEFAULT_SETTINGS
        self.assertEqual(sis.get_icon(), icon_const.EMPTY_STRING)
        self.assertEqual(sis.get_color(), icon_const.DEFAULT_ICON_COLOR)
        self.assertEqual(sis.get_scale(), icon_const.DEFAULT_ICON_SCALE)
        self.assertEqual(sis.get_opacity(), icon_const.DEFAULT_ICON_OPACITY)
        self.action.set_settings.assert_called()

    def test_scale_and_opacity_are_int(self):
        self.settings_data[icon_const.SETTING_ICON][icon_const.SETTING_SCALE] = 99.7
        self.settings_data[icon_const.SETTING_ICON][icon_const.SETTING_OPACITY] = 56.4
        self.action.get_settings.return_value = self.settings_data.copy()
        sis = icon_settings.ShowIconSettings(self.action)
        self.assertEqual(sis.get_scale(), 99)
        self.assertEqual(sis.get_opacity(), 56)


if __name__ == "__main__":
    unittest.main()