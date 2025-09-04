import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)


# Patch gi.repository.Gdk.RGBA so tests work without GTK installed
with patch("gi.repository.Gdk.RGBA") as MockRGBA:
    from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_helper

class TestCustomizationHelper(unittest.TestCase):
    def setUp(self):
        # Patch inside setUp so that RGBA is a MagicMock for every test
        self.rgba_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_helper.RGBA")
        self.MockRGBA = self.rgba_patch.start()

    def tearDown(self):
        self.rgba_patch.stop()

    def test_convert_color_list_to_rgba(self):
        # Arrange
        color = (255, 128, 64, 0)
        mock_rgba_instance = MagicMock()
        self.MockRGBA.return_value = mock_rgba_instance

        # Act
        result = customization_helper.convert_color_list_to_rgba(color)

        # Assert
        self.MockRGBA.assert_called_once()
        self.assertEqual(mock_rgba_instance.red, 1)
        self.assertEqual(mock_rgba_instance.green, 128/255)
        self.assertEqual(mock_rgba_instance.blue, 64/255)
        self.assertEqual(mock_rgba_instance.alpha, 1)
        self.assertIs(result, mock_rgba_instance)

    def test_convert_rgba_to_color_list(self):
        # Arrange
        mock_rgba = MagicMock()
        mock_rgba.red = 0.5
        mock_rgba.green = 0.25
        mock_rgba.blue = 0.75
        mock_rgba.alpha = 0.5  # Should be ignored

        # Act
        color_tuple = customization_helper.convert_rgba_to_color_list(mock_rgba)

        # Assert
        self.assertEqual(color_tuple, (127, 63, 191, 255))

    def test_convert_color_list_to_hex(self):
        # Act & Assert
        self.assertEqual(customization_helper.convert_color_list_to_hex((255, 128, 64, 0)), "#FF8040")
        self.assertEqual(customization_helper.convert_color_list_to_hex((0, 0, 0, 255)), "#000000")
        self.assertEqual(customization_helper.convert_color_list_to_hex((16, 32, 48, 255)), "#102030")
        # Ensure rounding works
        self.assertEqual(customization_helper.convert_color_list_to_hex((254.9, 128.7, 64.2, 0)), "#FE8040")