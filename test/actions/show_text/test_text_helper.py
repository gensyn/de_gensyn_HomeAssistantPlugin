import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, call


absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.customization_core import customization_const
from de_gensyn_HomeAssistantPlugin.actions.show_text import text_const, text_helper


class TestTextCustomization(unittest.TestCase):

    def test_get_text_not_connected(self):
        settings = Mock()
        settings.get_position.return_value = "top-left"
        settings.get_text_size.return_value = 12
        settings.get_text_color.return_value = (255, 255, 255, 255)
        settings.get_outline_size.return_value = 1
        settings.get_outline_color.return_value = (0, 0, 0, 255)

        result = text_helper.get_text(None, settings, False)

        self.assertEqual("N/A", result[0])
        self.assertEqual("top-left", result[1])
        self.assertEqual(12, result[2])
        self.assertEqual((255, 255, 255, 255), result[3])
        self.assertEqual(1, result[4])
        self.assertEqual((0, 0, 0, 255), result[5])

        settings.get_attribute.assert_not_called()

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.show_text.text_helper.log.error')
    @patch('de_gensyn_HomeAssistantPlugin.actions.show_text.text_helper._get_text')
    @patch('de_gensyn_HomeAssistantPlugin.actions.show_text.text_helper.get_value')
    @patch('de_gensyn_HomeAssistantPlugin.actions.show_text.text_helper._replace_values')
    def test_get_text_success(self, replace_values_mock, get_value_mock, get_text_mock, log_mock):
        settings = Mock()
        settings.get_position.return_value = "top-left"
        settings.get_text_size.return_value = 12
        settings.get_text_color.return_value = (255, 255, 255, 255)
        settings.get_outline_size.return_value = 1
        settings.get_outline_color.return_value = (0, 0, 0, 255)
        settings.get_attribute.return_value = "state"
        settings.get_round.return_value = False
        settings.get_round_precision.return_value = 0
        settings.get_show_unit.return_value = False
        settings.get_unit_line_break.return_value = False

        get_text_mock.side_effect = ("Initial Text", "1")

        get_value_mock.side_effect = ["on", "off", 1.5, 3.6]

        customization_not_float = Mock()
        customization_not_float.get_value.return_value = "on"
        customization_not_float.get_operator.return_value = "=="

        customization_value_not_float = Mock()
        customization_value_not_float.get_value.return_value = 0.0
        customization_value_not_float.get_operator.return_value = ">"

        customization_custom_value_error = Mock()
        customization_custom_value_error.get_value.return_value = "invalid_float"
        customization_custom_value_error.get_operator.return_value = ">"

        customization_float = Mock()
        customization_float.get_value.return_value = 3.7
        customization_float.get_operator.return_value = "<"

        settings.get_customizations.return_value = [customization_not_float, customization_value_not_float,
                                                    customization_custom_value_error, customization_float]

        replace_values_mock.side_effect = [("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"),
                                           ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11")]

        result = text_helper.get_text({"state": "state"}, settings, True)

        replace_values_mock.assert_has_calls([
            call("Initial Text", "top-left", "state", False, 0, 12, (255, 255, 255, 255), 1, (0, 0, 0, 255), False,
                 False, customization_not_float),
            call("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", customization_float)
        ])
        log_mock.assert_called_once_with("Could not convert custom value to float: %s", "invalid_float")
        self.assertEqual("1", result[0])
        self.assertEqual("2", result[1])
        self.assertEqual("6", result[2])
        self.assertEqual("7", result[3])
        self.assertEqual("8", result[4])
        self.assertEqual("9", result[5])

    def test_get_value_state(self):
        settings = Mock()
        settings.get_attribute.return_value = "state"
        settings.get_round.return_value = False
        settings.get_round_precision.return_value = 3
        settings.get_show_unit.return_value = True

        state = {"state": "on"}

        customization = Mock()
        customization.get_attribute.return_value = "state"

        result = text_helper.get_value(state, settings, customization)

        self.assertEqual("on", result)

    @patch('de_gensyn_HomeAssistantPlugin.actions.show_text.text_helper._get_text')
    def test_get_value_text_length(self, get_text_mock):
        settings = Mock()
        settings.get_attribute.return_value = "state"
        settings.get_round.return_value = False
        settings.get_round_precision.return_value = 3
        settings.get_show_unit.return_value = True

        get_text_mock.return_value = "some_text"

        state = {"state": "on"}

        customization = Mock()
        customization.get_attribute.return_value = text_const.CUSTOM_TEXT_LENGTH

        result = text_helper.get_value(state, settings, customization)

        get_text_mock.assert_called_once_with(state, "state", False, 3, True, False)
        self.assertEqual(len("some_text"), result)

    def test_get_value_attribute(self):
        settings = Mock()
        settings.get_attribute.return_value = "state"
        settings.get_round.return_value = False
        settings.get_round_precision.return_value = 3
        settings.get_show_unit.return_value = True

        state = {
            "state": "on",
            customization_const.ATTRIBUTES: {
                "volume": 123
            }
        }

        customization = Mock()
        customization.get_attribute.return_value = "volume"

        result = text_helper.get_value(state, settings, customization)

        self.assertEqual(123, result)

    def test_get_text_state_no_unit(self):
        state = {"state": "23.5678"}
        attribute = text_const.STATE
        text_round = True
        round_precision = 2
        show_unit = False
        line_break = True

        result = text_helper._get_text(state, attribute, text_round, round_precision, show_unit, line_break)

        self.assertEqual("23.57", result)

    def test_get_text_state_unit_no_break(self):
        state = {
            "state": "23.5678",
            customization_const.ATTRIBUTES: {
                customization_const.UNIT_OF_MEASUREMENT: "°C"
            }
        }
        attribute = text_const.STATE
        text_round = True
        round_precision = 2
        show_unit = True
        line_break = False

        result = text_helper._get_text(state, attribute, text_round, round_precision, show_unit, line_break)

        self.assertEqual("23.57 °C", result)

    def test_get_text_state_unit_break(self):
        state = {
            "state": "23.5678",
            customization_const.ATTRIBUTES: {
                customization_const.UNIT_OF_MEASUREMENT: "°C"
            }
        }
        attribute = text_const.STATE
        text_round = True
        round_precision = 2
        show_unit = True
        line_break = True

        result = text_helper._get_text(state, attribute, text_round, round_precision, show_unit, line_break)

        self.assertEqual("23.57\n°C", result)

    def test_get_text_attribute(self):
        state = {
            "state": "23.5678",
            customization_const.ATTRIBUTES: {
                "volume": 4.358
            }
        }
        attribute = "volume"
        text_round = False
        round_precision = 1
        show_unit = False
        line_break = False

        result = text_helper._get_text(state, attribute, text_round, round_precision, show_unit, line_break)

        self.assertEqual("4.358", result)

    def test_replace_values(self):
        text = "Value: %s"
        position = "top"
        attribute = "state"
        text_round = True
        round_precision = 2
        text_size = 15
        text_color = (255, 255, 255, 255)
        outline_size = 1
        outline_color = (0, 0, 0, 255)
        show_unit = True
        line_break = False

        customization = Mock()
        customization.get_custom_text.return_value = "Custom: %s"
        customization.get_position.return_value = "bottom"
        customization.get_text_attribute.return_value = "volume"
        customization.get_round.return_value = False
        customization.get_round_precision.return_value = 3
        customization.get_text_size.return_value = 20
        customization.get_text_color.return_value = (200, 200, 200, 255)
        customization.get_outline_size.return_value = 2
        customization.get_outline_color.return_value = (50, 50, 50, 255)
        customization.get_show_unit.return_value = False
        customization.get_line_break.return_value = True

        result = text_helper._replace_values(text, position, attribute, text_round,
                                            round_precision, text_size, text_color,
                                            outline_size, outline_color, show_unit,
                                            line_break, customization)

        self.assertEqual("Custom: Value: %s", result[0])
        self.assertEqual("bottom", result[1])
        self.assertEqual("volume", result[2])
        self.assertEqual(False, result[3])
        self.assertEqual(3, result[4])
        self.assertEqual(20, result[5])
        self.assertEqual((200, 200, 200, 255), result[6])
        self.assertEqual(2, result[7])
        self.assertEqual((50, 50, 50, 255), result[8])
        self.assertEqual(False, result[9])
        self.assertEqual(True, result[10])

    def test_round_value_not_is_round(self):
        text = "3.14159"
        is_round = False
        precision = 2

        result = text_helper._round_value(text, is_round, precision)

        self.assertEqual("3.14159", result)

    def test_round_value_not_is_float(self):
        text = "not_a_number"
        is_round = False
        precision = 2

        result = text_helper._round_value(text, is_round, precision)

        self.assertEqual("not_a_number", result)

    def test_round_value_precision_not_zero(self):
        text = "3.14159"
        is_round = True
        precision = 2

        result = text_helper._round_value(text, is_round, precision)

        self.assertEqual("3.14", result)

    def test_round_value_precision_zero(self):
        text = "3.14159"
        is_round = True
        precision = 0

        result = text_helper._round_value(text, is_round, precision)

        self.assertEqual("3", result)

    def test_is_float_string_no_dot(self):
        value = "abc"

        result = text_helper._is_float(value)

        self.assertFalse(result)

    def test_is_float_number_no_dot(self):
        value = "53"

        result = text_helper._is_float(value)

        self.assertFalse(result)

    def test_is_float_string_dot(self):
        value = "ab.c"

        result = text_helper._is_float(value)

        self.assertFalse(result)

    def test_is_float_number_dot(self):
        value = "5.3"

        result = text_helper._is_float(value)

        self.assertTrue(result)