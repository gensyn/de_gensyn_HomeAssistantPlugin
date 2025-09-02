import sys
import unittest
from pathlib import Path

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization


class TestCustomization(unittest.TestCase):
    def test_getters(self):
        cust = customization.Customization("temperature", ">", "20")
        self.assertEqual(cust.get_attribute(), "temperature")
        self.assertEqual(cust.get_operator(), ">")
        self.assertEqual(cust.get_value(), "20")

    def test_export_not_implemented(self):
        cust = customization.Customization("humidity", "<", "50")
        with self.assertRaises(NotImplementedError):
            cust.export()
