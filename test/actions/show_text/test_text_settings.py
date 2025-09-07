import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_const
from de_gensyn_HomeAssistantPlugin.actions.show_text import text_settings, text_const
from de_gensyn_HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from de_gensyn_HomeAssistantPlugin.actions.show_text.text_settings import ShowTextSettings


class TestShowTextSettings(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.show_text.text_settings.CustomizationSettings.__init__', autospec=True)
    def test_init_values_present(self, super_init_mock):
        action = Mock()
        action.get_settings.return_value = {
            text_const.SETTING_TEXT: {
                text_const.SETTING_POSITION: "top-left",
                text_const.SETTING_ATTRIBUTE: "state",
                text_const.SETTING_ROUND: True,
                text_const.SETTING_ROUND_PRECISION: 2,
                text_const.SETTING_TEXT_SIZE: 100,
                text_const.SETTING_TEXT_COLOR: (255, 255, 255, 255),
                text_const.SETTING_OUTLINE_SIZE: 2,
                text_const.SETTING_OUTLINE_COLOR: (0, 0, 0, 255),
                text_const.SETTING_SHOW_UNIT: True,
                text_const.SETTING_UNIT_LINE_BREAK: False,
                customization_const.SETTING_CUSTOMIZATIONS: []
            }
        }

        def super_init(instance, action, _, __):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = ShowTextSettings(action)

        super_init_mock.assert_called_once_with(instance, action, text_const.SETTING_TEXT, TextCustomization) # with instance because of autospec
        action.set_settings.assert_not_called()
        self.assertEqual("top-left", instance.get_position())
        self.assertEqual("state", instance.get_attribute())
        self.assertTrue(instance.get_round())
        self.assertEqual(2, instance.get_round_precision())
        self.assertEqual(100, instance.get_text_size())
        self.assertEqual((255, 255, 255, 255), instance.get_text_color())
        self.assertEqual(2, instance.get_outline_size())
        self.assertEqual((0, 0, 0, 255), instance.get_outline_color())
        self.assertTrue(instance.get_show_unit())
        self.assertFalse(instance.get_unit_line_break())

    @patch('de_gensyn_HomeAssistantPlugin.actions.show_text.text_settings.CustomizationSettings.__init__', autospec=True)
    def test_init_with_defaults(self, super_init_mock):
        action = Mock()
        action.get_settings.return_value = {}

        def super_init(instance, action, _, __):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = ShowTextSettings(action)

        super_init_mock.assert_called_once_with(instance, action, text_const.SETTING_TEXT, TextCustomization) # with instance because of autospec
        self.assertEqual(text_const.DEFAULT_POSITION, instance.get_position())
        self.assertEqual(text_const.STATE, instance.get_attribute())
        self.assertEqual(text_const.DEFAULT_ROUND, instance.get_round())
        self.assertEqual(text_const.DEFAULT_ROUND_PRECISION, instance.get_round_precision())
        self.assertEqual(text_const.DEFAULT_TEXT_SIZE, instance.get_text_size())
        self.assertEqual(text_const.DEFAULT_TEXT_COLOR, instance.get_text_color())
        self.assertEqual(text_const.DEFAULT_OUTLINE_SIZE, instance.get_outline_size())
        self.assertEqual(text_const.DEFAULT_OUTLINE_COLOR, instance.get_outline_color())
        self.assertEqual(text_const.DEFAULT_SHOW_UNIT, instance.get_show_unit())
        self.assertEqual(text_const.DEFAULT_UNIT_LINE_BREAK, instance.get_unit_line_break())