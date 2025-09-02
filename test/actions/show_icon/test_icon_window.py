import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import gi
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_window, icon_const
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization


def _add_window_widgets(win):
    # Patch instance attributes that are not created by our patching
    win.entry_value = MagicMock()
    win.icon = MagicMock()
    win.check_icon = MagicMock()
    win.color = MagicMock()
    win.check_color = MagicMock()
    win.scale = MagicMock()
    win.check_scale = MagicMock()
    win.scale_entry = MagicMock()
    win.opacity = MagicMock()
    win.check_opacity = MagicMock()
    win.opacity_entry = MagicMock()


class TestIconWindow(unittest.TestCase):
    def setUp(self):
        # Patch all GUI and helper methods
        patcher_icons = patch.object(icon_window.icon_helper, "MDI_ICONS", {"testicon": "M0,0"})
        self.real_rgba = Gdk.RGBA()
        self.real_rgba.red = 1.0
        self.real_rgba.green = 0.0
        self.real_rgba.blue = 0.0
        self.real_rgba.alpha = 1.0
        patcher_convert_color_list_to_rgba = patch(
            "de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_helper.convert_color_list_to_rgba",
            return_value=self.real_rgba
        )
        patcher_convert_rgba_to_color_list = patch("de_gensyn_HomeAssistantPlugin.actions.cores.customization_core.customization_helper.convert_rgba_to_color_list", return_value=[1,2,3,4])

        self.addCleanup(patcher_icons.stop)
        self.addCleanup(patcher_convert_color_list_to_rgba.stop)
        self.addCleanup(patcher_convert_rgba_to_color_list.stop)
        patcher_icons.start()
        patcher_convert_color_list_to_rgba.start()
        patcher_convert_rgba_to_color_list.start()

        # Prepare a minimal lm (localization manager) mock
        self.lm = MagicMock()
        self.lm.get.side_effect = lambda k: k

        # Prepare callback mock
        self.callback = MagicMock()

        # Attributes for the window
        self.attributes = ["temperature", "humidity"]

    def test_icon_window_init(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        _add_window_widgets(win)
        self.assertIsInstance(win.icons, list)
        self.assertIn("testicon", win.icons)

    def test_set_default_values(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        _add_window_widgets(win)
        win.default_margin = 5
        win._set_default_values()
        win.color.set_rgba.assert_called_with(self.real_rgba)
        win.scale.set_value.assert_called_with(icon_const.DEFAULT_ICON_SCALE)
        win.scale_entry.set_text.assert_called_with(str(icon_const.DEFAULT_ICON_SCALE))
        win.opacity.set_value.assert_called_with(icon_const.DEFAULT_ICON_OPACITY)
        win.opacity_entry.set_text.assert_called_with(str(icon_const.DEFAULT_ICON_OPACITY))

    def test_set_current_values(self):
        # Create a customization object
        customization = MagicMock(spec=IconCustomization)
        customization.get_icon.return_value = "testicon"
        customization.get_color.return_value = [1, 2, 3, 4]
        customization.get_scale.return_value = 42
        customization.get_opacity.return_value = 77

        with patch.object(icon_window.CustomizationWindow, "_set_current_values"):
            win = icon_window.IconWindow(self.lm, self.attributes, self.callback, current=customization)
        _add_window_widgets(win)
        win._set_current_values()
        win.icon.set_text.assert_called_with("testicon")
        win.check_icon.set_active.assert_called_with(True)
        win.color.set_rgba.assert_called_with(self.real_rgba)
        win.check_color.set_active.assert_called_with(True)
        win.scale.set_value.assert_called_with(42)
        win.check_scale.set_active.assert_called_with(True)
        win.scale_entry.set_text.assert_called_with("42")
        win.opacity.set_value.assert_called_with(77)
        win.check_opacity.set_active.assert_called_with(True)
        win.opacity_entry.set_text.assert_called_with("77")

    def test_set_current_values_none(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        result = win._set_current_values()
        self.assertIsNone(result)

    def test_on_add_button_valid(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        _add_window_widgets(win)
        # Patch super()._on_add_button to return True
        with patch.object(icon_window.CustomizationWindow, "_on_add_button", return_value=True):
            # Setup icon entry with valid mdi icon
            win.check_icon.get_active.return_value = True
            win.icon.get_text.return_value = "mdi:testicon"
            win.icons = ["testicon"]
            # Set operator not needing float conversion
            win.operator = MagicMock()
            win.operator.get_model.return_value = [["=="]]
            win.operator.get_active.return_value = 0
            win.entry_value.get_text.return_value = "someval"
            win.condition_attribute = MagicMock()
            win.condition_attribute.get_model.return_value = [["attr"]]
            win.condition_attribute.get_active.return_value = 0
            # Set checks for color/scale/opacity inactive; only icon active
            win.check_color.get_active.return_value = False
            win.check_scale.get_active.return_value = False
            win.check_opacity.get_active.return_value = False
            # Setup style_context mocks
            win.icon.get_style_context.return_value = MagicMock()
            win.check_icon.get_style_context.return_value = MagicMock()
            win.check_color.get_style_context.return_value = MagicMock()
            win.check_scale.get_style_context.return_value = MagicMock()
            win.check_opacity.get_style_context.return_value = MagicMock()
            # Patch destroy
            win.destroy = MagicMock()
            # Patch IconCustomization constructor
            with patch.object(icon_window, "IconCustomization") as mock_icon_custom:
                win.callback = MagicMock()
                win._on_add_button(None)
                mock_icon_custom.assert_called()
                win.callback.assert_called()
                win.destroy.assert_called()

    def test_on_add_button_icon_not_in_list(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        _add_window_widgets(win)
        with patch.object(icon_window.CustomizationWindow, "_on_add_button", return_value=True):
            win.check_icon.get_active.return_value = True
            win.icon.get_text.return_value = "mdi:notfound"
            win.icons = ["testicon"]
            # Setup style_context mock for error
            win.icon.get_style_context.return_value = MagicMock()
            win.icon.add_css_class = MagicMock()
            win._on_add_button(None)
            win.icon.add_css_class.assert_called_with(icon_const.ERROR)

    def test_on_add_button_no_checks_active(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        _add_window_widgets(win)
        with patch.object(icon_window.CustomizationWindow, "_on_add_button", return_value=True):
            win.check_icon.get_active.return_value = False
            win.check_color.get_active.return_value = False
            win.check_scale.get_active.return_value = False
            win.check_opacity.get_active.return_value = False
            # Setup style_context mock for error
            for widget in [win.check_icon, win.check_color, win.check_scale, win.check_opacity]:
                widget.get_style_context.return_value = MagicMock()
                widget.add_css_class = MagicMock()
            win._on_add_button(None)
            for widget in [win.check_icon, win.check_color, win.check_scale, win.check_opacity]:
                widget.add_css_class.assert_called_with(icon_const.ERROR)

    def test_on_add_button_operator_expects_number_but_invalid(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        _add_window_widgets(win)
        with patch.object(icon_window.CustomizationWindow, "_on_add_button", return_value=True):
            # Setup for operator needing float conversion
            win.check_icon.get_active.return_value = True
            win.icon.get_text.return_value = "mdi:testicon"
            win.icons = ["testicon"]
            win.operator = MagicMock()
            win.operator.value = "<"
            win.operator.get_selected_item.return_value = win.operator
            win.entry_value.get_text.return_value = "not_a_number"
            win.operator.get_style_context.return_value = MagicMock()
            win.operator.add_css_class = MagicMock()
            win.entry_value.get_style_context.return_value = MagicMock()
            win.entry_value.add_css_class = MagicMock()
            win._on_add_button(None)
            win.operator.add_css_class.assert_called_with(icon_const.ERROR)
            win.entry_value.add_css_class.assert_called_with(icon_const.ERROR)

    def test_on_widget_changed(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        win.icon = MagicMock()
        win.check_icon = MagicMock()
        win.check_color = MagicMock()
        win.check_scale = MagicMock()
        win.check_opacity = MagicMock()
        # Patch their style_context
        for widget in [win.icon, win.check_icon, win.check_color, win.check_scale, win.check_opacity]:
            widget.get_style_context.return_value = MagicMock()
            widget.remove_css_class = MagicMock()
        win._on_widget_changed(None)
        for widget in [win.icon, win.check_icon, win.check_color, win.check_scale, win.check_opacity]:
            widget.remove_css_class.assert_called_with(icon_const.ERROR)

    def test_on_add_button_super_returns_false(self):
        win = icon_window.IconWindow(self.lm, self.attributes, self.callback)
        _add_window_widgets(win)
        # Patch super()._on_add_button to return False
        with patch.object(icon_window.CustomizationWindow, "_on_add_button", return_value=False):
            # Patch destroy and callback to check they are NOT called
            win.destroy = MagicMock()
            win.callback = MagicMock()
            win._on_add_button(None)
            win.destroy.assert_not_called()
            win.callback.assert_not_called()
