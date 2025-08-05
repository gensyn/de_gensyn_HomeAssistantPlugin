import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.main import HomeAssistant


class TestMainOnChangeBaseSwitch(unittest.TestCase):

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.PerformAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.ActionHolder")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantBackend")
    @patch("de_gensyn_HomeAssistantPlugin.main.ConnectionSettings")
    def test_on_change_base_switch_active(self, settings_mock, _, __, ___, ____, _____, ______):
        set_setting_mock = Mock()

        settings_mock.return_value = settings_mock
        settings_mock.set_setting = set_setting_mock
        settings_mock.get_verify_certificate = lambda: True

        set_sensitive_mock = Mock()
        set_active_mock = Mock()

        verify_certificate_switch_mock = Mock()
        verify_certificate_switch_mock.set_sensitive = set_sensitive_mock
        verify_certificate_switch_mock.set_active = set_active_mock

        entry = "ssl"

        test_bool = True

        entry_mock = Mock()
        entry_mock.get_active = lambda: test_bool

        instance = HomeAssistant()
        instance.verify_certificate_switch = verify_certificate_switch_mock
        instance._on_change_base_switch(entry_mock, None, entry)

        set_setting_mock.assert_called_once_with(entry, test_bool)
        set_sensitive_mock.assert_called_once_with(True)
        set_active_mock.assert_called_once_with(True)

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.PerformAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.ActionHolder")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantBackend")
    @patch("de_gensyn_HomeAssistantPlugin.main.ConnectionSettings")
    def test_on_change_base_switch_not_active(self, settings_mock, _, __, ___, ____, _____, ______):
        set_setting_mock = Mock()

        settings_mock.return_value = settings_mock
        settings_mock.set_setting = set_setting_mock

        set_sensitive_mock = Mock()
        set_active_mock = Mock()

        verify_certificate_switch_mock = Mock()
        verify_certificate_switch_mock.set_sensitive = set_sensitive_mock
        verify_certificate_switch_mock.set_active = set_active_mock

        entry = "ssl"

        test_bool = False

        entry_mock = Mock()
        entry_mock.get_active = lambda: test_bool

        instance = HomeAssistant()
        instance.verify_certificate_switch = verify_certificate_switch_mock
        instance._on_change_base_switch(entry_mock, None, entry)

        set_setting_mock.assert_called_once_with(entry, test_bool)
        set_sensitive_mock.assert_called_once_with(False)
        set_active_mock.assert_called_once_with(False)


if __name__ == '__main__':
    unittest.main()
