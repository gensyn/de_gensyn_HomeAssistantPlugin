import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_row, icon_const
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization

class TestIconRow(unittest.TestCase):
    def setUp(self):
        self.lm = MagicMock()
        self.lm.get.side_effect = lambda x: {
            icon_const.LABEL_ICON_ICON: "Icon:",
            icon_const.LABEL_ICON_COLOR: "Color:",
            icon_const.LABEL_ICON_SCALE: "Scale:",
            icon_const.LABEL_ICON_OPACITY: "Opacity:",
            'actions.home_assistant.customization.greater_than.label': "Greater Than",
        }.get(x, x)
        self.customization = MagicMock(spec=IconCustomization)
        self.customization.get_icon.return_value = "mdi:thermometer"
        self.customization.get_color.return_value = (255, 0, 0, 255)
        self.customization.get_scale.return_value = 2
        self.customization.get_opacity.return_value = 150
        self.customization.get_attribute.return_value = "temperature"
        self.customization.get_operator.return_value = ">"
        self.customization.get_value.return_value = "20"
        self.customization_count = 1
        self.index = 0
        self.attributes = ["temperature"]
        self.state = {"attributes": {"temperature": "23"}}
        self.settings = MagicMock()
        # Patch convert_color_list_to_hex
        patcher = unittest.mock.patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_helper.convert_color_list_to_hex", return_value="#FF0000FF")
        self.addCleanup(patcher.stop)
        self.mock_convert_color = patcher.start()

    def test_icon_row_title(self):
        with unittest.mock.patch.object(icon_row.CustomizationRow, "set_title"):
            row = icon_row.IconRow(
                self.lm,
                self.customization,
                self.customization_count,
                self.index,
                self.attributes,
                self.state,
                self.settings,
            )
            # The set_title method should be called with a string containing all components.
            title_arg = row.set_title.call_args[0][0]
            self.assertIn("Icon: mdi:thermometer", title_arg)
            self.assertIn("Color: #FF0000FF", title_arg)
            self.assertIn("Scale: 2", title_arg)
            self.assertIn("Opacity: 150", title_arg)

    def test_icon_row_title_partial(self):
        # Only icon and color set
        self.customization.get_scale.return_value = None
        self.customization.get_opacity.return_value = None

        with unittest.mock.patch.object(icon_row.CustomizationRow, "set_title"):
            row = icon_row.IconRow(
                self.lm,
                self.customization,
                self.customization_count,
                self.index,
                self.attributes,
                self.state,
                self.settings,
            )
            title_arg = row.set_title.call_args[0][0]
            self.assertIn("Icon: mdi:thermometer", title_arg)
            self.assertIn("Color: #FF0000FF", title_arg)
            self.assertNotIn("Scale:", title_arg)
            self.assertNotIn("Opacity:", title_arg)

    def test_icon_row_title_none(self):
        # All customization values None
        self.customization.get_icon.return_value = None
        self.customization.get_color.return_value = None
        self.customization.get_scale.return_value = None
        self.customization.get_opacity.return_value = None

        with unittest.mock.patch.object(icon_row.CustomizationRow, "set_title"):
            row = icon_row.IconRow(
                self.lm,
                self.customization,
                self.customization_count,
                self.index,
                self.attributes,
                self.state,
                self.settings,
            )
            title_arg = row.set_title.call_args[0][0]
            self.assertNotIn("Icon:", title_arg)
            self.assertNotIn("Color:", title_arg)
            self.assertNotIn("Scale:", title_arg)
            self.assertNotIn("Opacity:", title_arg)