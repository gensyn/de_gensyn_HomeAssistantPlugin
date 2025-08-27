import sys
import unittest
from pathlib import Path

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_customization
from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_const
from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_const

class TestIconCustomization(unittest.TestCase):
    def setUp(self):
        self.attribute = "temperature"
        self.operator = ">"
        self.value = "20"
        self.icon = "mdi:thermometer"
        self.color = (255, 0, 0, 255)
        self.scale = 2
        self.opacity = 150
        self.customization_dict = {
            customization_const.CONDITION: {
                customization_const.ATTRIBUTE: self.attribute,
                customization_const.OPERATOR: self.operator,
                customization_const.VALUE: self.value,
            },
            icon_const.CUSTOM_ICON: self.icon,
            icon_const.CUSTOM_COLOR: self.color,
            icon_const.CUSTOM_SCALE: self.scale,
            icon_const.CUSTOM_OPACITY: self.opacity,
        }

    def test_init_and_getters(self):
        icon_cust = icon_customization.IconCustomization(
            self.attribute, self.operator, self.value, self.icon, self.color, self.scale, self.opacity
        )
        self.assertEqual(icon_cust.get_icon(), self.icon)
        self.assertEqual(icon_cust.get_color(), self.color)
        self.assertEqual(icon_cust.get_scale(), self.scale)
        self.assertEqual(icon_cust.get_opacity(), self.opacity)

    def test_export(self):
        icon_cust = icon_customization.IconCustomization(
            self.attribute, self.operator, self.value, self.icon, self.color, self.scale, self.opacity
        )
        self.assertEqual(icon_cust.export(), self.customization_dict)

    def test_from_dict(self):
        icon_cust = icon_customization.IconCustomization.from_dict(self.customization_dict)
        self.assertEqual(icon_cust.get_icon(), self.icon)
        self.assertEqual(icon_cust.get_color(), self.color)
        self.assertEqual(icon_cust.get_scale(), self.scale)
        self.assertEqual(icon_cust.get_opacity(), self.opacity)
        self.assertEqual(icon_cust.get_attribute(), self.attribute)
        self.assertEqual(icon_cust.get_operator(), self.operator)
        self.assertEqual(icon_cust.get_value(), self.value)