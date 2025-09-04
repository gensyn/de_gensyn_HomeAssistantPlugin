import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.show_icon import icon_const
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_row import IconRow
from de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization

class TestIconRow(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_row.CustomizationRow.__init__', autospec=True)
    @patch('de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_row.icon_helper')
    @patch('de_gensyn_HomeAssistantPlugin.actions.show_icon.icon_row.customization_helper')
    @patch.object(IconRow, '_init_title')
    @patch.object(IconRow, 'set_title')
    def test_init(self, set_title_mock, init_title_mock, customization_helper_mock, icon_helper_mock, super_init_mock):
        lm = {
            icon_const.LABEL_ICON_ICON: "Icon",
            icon_const.LABEL_ICON_COLOR: "Color",
            icon_const.LABEL_ICON_SCALE: "Scale",
            icon_const.LABEL_ICON_OPACITY: "Opacity"
        }

        def super_init(instance, lm, *args, **kwargs):
            instance.lm = lm

        super_init_mock.side_effect = super_init
        init_title_mock.return_value = "Title"
        icon_helper_mock.get_value.return_value = "current_value"
        customization_helper_mock.convert_color_list_to_hex.return_value = "#FF0000"

        customization_mock = Mock()
        customization_mock.get_icon.return_value = "icon_name"
        customization_mock.get_color.return_value = [255, 0, 0]
        customization_mock.get_scale.return_value = 150
        customization_mock.get_opacity.return_value = 80
        customization_count = 5
        index = 3
        attributes = ['attr1', 'attr2']
        state = {'state_key': 'state_value'}
        settings = "settings"

        instance = IconRow(lm, customization_mock, customization_count, index, attributes, state, settings)

        super_init_mock.assert_called_once_with(instance, lm, customization_count, index, attributes, state, settings) # with instance because of autospec
        icon_helper_mock.get_value.assert_called_once_with(state, customization_mock)
        init_title_mock.assert_called_once_with(customization_mock, "current_value")
        set_title_mock.assert_called_once_with(
            "Title\nIcon icon_name\nColor #FF0000\nScale 150\nOpacity 80"
        )