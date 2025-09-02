import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

class TestCustomizationRow(unittest.TestCase):
    def setUp(self):
        # Patch GTK/Adw widgets but NOT ActionRow
        self.button_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_row.Button")
        self.align_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_row.Align")
        self.box_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_row.Box")
        self.orientation_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_row.Orientation")
        self.const_patch = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_row.customization_const")

        self.MockButton = self.button_patch.start()
        self.MockAlign = self.align_patch.start()
        self.MockBox = self.box_patch.start()
        self.MockOrientation = self.orientation_patch.start()
        self.mock_const = self.const_patch.start()
        self.mock_const.LABEL_CUSTOMIZATION_OPERATORS = {"eq": "equals", "gt": "greater"}
        self.mock_const.LABEL_CUSTOMIZATION_IF = "If"
        self.mock_const.LABEL_CUSTOMIZATION_CURRENT = "Current"

        # Patch add_suffix method to avoid GTK widget type errors
        from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_row
        self.customization_row = customization_row
        self.add_suffix_patch = patch.object(
            self.customization_row.CustomizationRow, "add_suffix"
        )
        self.mock_add_suffix = self.add_suffix_patch.start()

        # Patch Button and Box to always return a new MagicMock every time
        def button_side_effect(*args, **kwargs):
            m = MagicMock()
            m.set_size_request = MagicMock()
            m.set_sensitive = MagicMock()
            return m
        self.MockButton.side_effect = button_side_effect

        def box_side_effect(*args, **kwargs):
            m = MagicMock()
            m.append = MagicMock()
            return m
        self.MockBox.side_effect = box_side_effect

        self.MockOrientation.VERTICAL = "vertical"
        self.MockAlign.CENTER = "center"

        # Create mocks for Customization and CustomizationSettings
        self.mock_customization = MagicMock()
        self.mock_customization.get_operator.return_value = "eq"
        self.mock_customization.get_attribute.return_value = "temperature"
        self.mock_customization.get_value.return_value = 23

        self.mock_settings = MagicMock()
        self.mock_lm = MagicMock()
        self.mock_lm.get.side_effect = lambda key: f"label-{key}"

        self.mock_state = {"temperature": 22}
        self.mock_attributes = ["temperature", "humidity"]

    def tearDown(self):
        self.button_patch.stop()
        self.align_patch.stop()
        self.box_patch.stop()
        self.orientation_patch.stop()
        self.const_patch.stop()
        self.add_suffix_patch.stop()

    def test_customization_row_buttons_setup(self):
        row = self.customization_row.CustomizationRow(
            lm=self.mock_lm,
            customization_count=3,
            index=1,
            attributes=self.mock_attributes,
            state=self.mock_state,
            settings=self.mock_settings
        )

        # Ensure buttons/boxes are created and assigned
        self.assertTrue(hasattr(row, 'edit_button'))
        self.assertTrue(hasattr(row, 'delete_button'))
        self.assertTrue(hasattr(row, 'up_button'))
        self.assertTrue(hasattr(row, 'down_button'))

        row.edit_button.set_size_request.assert_called_with(15, 15)
        row.delete_button.set_size_request.assert_called_with(15, 15)
        row.up_button.set_size_request.assert_called_with(15, 7)
        row.down_button.set_size_request.assert_called_with(15, 7)

        row.up_button.set_sensitive.assert_called_with(True)
        row.down_button.set_sensitive.assert_called_with(True)

        # Check that add_suffix was called with two boxes with .append method
        self.assertEqual(self.mock_add_suffix.call_count, 2)
        for call_args in self.mock_add_suffix.call_args_list:
            box_arg = call_args[0][0]
            self.assertTrue(hasattr(box_arg, 'append'))

        self.assertEqual(row.lm, self.mock_lm)
        self.assertEqual(row.attributes, self.mock_attributes)
        self.assertEqual(row.state, self.mock_state)
        self.assertEqual(row.settings, self.mock_settings)

    def test_customization_row_buttons_first_last(self):
        # First row (index=0)
        row1 = self.customization_row.CustomizationRow(
            lm=self.mock_lm,
            customization_count=3,
            index=0,
            attributes=self.mock_attributes,
            state=self.mock_state,
            settings=self.mock_settings
        )
        row1.up_button.set_sensitive.assert_called_with(False)
        row1.down_button.set_sensitive.assert_called_with(True)

        # Last row (index=customization_count-1)
        row2 = self.customization_row.CustomizationRow(
            lm=self.mock_lm,
            customization_count=3,
            index=2,
            attributes=self.mock_attributes,
            state=self.mock_state,
            settings=self.mock_settings
        )
        row2.up_button.set_sensitive.assert_called_with(True)
        row2.down_button.set_sensitive.assert_called_with(False)

    def test_init_title(self):
        row = self.customization_row.CustomizationRow(
            lm=self.mock_lm,
            customization_count=1,
            index=0,
            attributes=self.mock_attributes,
            state=self.mock_state,
            settings=self.mock_settings
        )

        title = row._init_title(self.mock_customization, current_value=22)
        self.assertIn("label-If", title)
        self.assertIn("\"temperature\"", title)
        self.assertIn("label-equals", title)
        self.assertIn("\"23\"", title)
        self.assertIn("(label-Current: 22):", title)

if __name__ == "__main__":
    unittest.main()