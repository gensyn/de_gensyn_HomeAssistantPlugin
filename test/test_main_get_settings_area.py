import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call, Mock

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.main import HomeAssistant
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestMainGetSettingsArea(unittest.TestCase):

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.PerformAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.ActionHolder")
    @patch("de_gensyn_HomeAssistantPlugin.main.EntryRow")
    @patch("de_gensyn_HomeAssistantPlugin.main.SwitchRow")
    @patch("de_gensyn_HomeAssistantPlugin.main.PreferencesGroup")
    @patch("de_gensyn_HomeAssistantPlugin.main.PasswordEntryRow")
    @patch("de_gensyn_HomeAssistantPlugin.main.ConnectionSettings")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantBackend")
    def test_reload_settings_success(self, backend_mock, settings_mock, password_entry_init_mock, group_init_mock,
                             switch_init_mock, entry_init_mock, _, __, ___, ____, _____):
        set_text_mock = Mock()
        set_active_mock = Mock()
        set_editable_mock = Mock()
        connect_mock = Mock()
        add_mock = Mock()

        entry_mock = Mock()
        entry_mock.set_text = set_text_mock
        entry_mock.set_editable = set_editable_mock
        entry_mock.connect = connect_mock
        entry_init_mock.return_value = entry_mock

        switch_mock = Mock()
        switch_mock.set_active = set_active_mock
        switch_mock.connect = connect_mock
        switch_init_mock.return_value = switch_mock

        password_entry_mock = Mock()
        password_entry_mock.set_text = set_text_mock
        password_entry_mock.connect = connect_mock
        password_entry_init_mock.return_value = password_entry_mock

        group_mock = Mock()
        group_mock.add = add_mock
        group_init_mock.return_value = group_mock

        label_host = "Host"
        label_port = "Port"
        label_ssl = "SSL"
        label_verify_certificate = "Verify Certificate"
        label_token = "Token"

        locale_mock = {
            const.LABEL_HOST: label_host,
            const.LABEL_PORT: label_port,
            const.LABEL_SSL: label_ssl,
            const.LABEL_VERIFY_CERTIFICATE: label_verify_certificate,
            const.LABEL_TOKEN: label_token
        }

        host = "localhost"
        port = "8123"
        ssl = True
        verify_certificate = False
        token = "abc"

        settings_mock.return_value = settings_mock
        settings_mock.get_host = lambda: host
        settings_mock.get_port = lambda: port
        settings_mock.get_ssl = lambda: ssl
        settings_mock.get_verify_certificate = lambda: verify_certificate
        settings_mock.get_token = lambda: token

        connection_status_callback_mock = Mock()

        backend_mock.is_connected = lambda: True
        backend_mock.set_connection_status_callback = connection_status_callback_mock

        instance = HomeAssistant()
        instance.backend = backend_mock
        instance.locale_manager = locale_mock
        result = instance.get_settings_area()

        self.assertEqual(group_mock, result)

        self.assertEqual(3, entry_init_mock.call_count)
        self.assertEqual(entry_init_mock.call_args_list,
                         [call(title=label_host), call(title=label_port), call(title="Connection status:")])

        self.assertEqual(2, switch_init_mock.call_count)
        self.assertEqual(switch_init_mock.call_args_list, [call(title=label_ssl), call(title=label_verify_certificate)])

        self.assertEqual(1, password_entry_init_mock.call_count)
        self.assertEqual(password_entry_init_mock.call_args_list, [call(title=label_token)])

        self.assertEqual(4, set_text_mock.call_count)
        set_text_mock.assert_has_calls([
            call(host),
            call(port),
            call(token),
            call(backend_const.CONNECTED)
        ])

        self.assertEqual(2, set_active_mock.call_count)
        set_active_mock.assert_has_calls([
            call(ssl),
            call(verify_certificate)
        ])

        self.assertEqual(1, set_editable_mock.call_count)
        set_editable_mock.assert_has_calls([call(False)])

        self.assertEqual(1, connection_status_callback_mock.call_count)
        connection_status_callback_mock.assert_called_once_with(instance.set_status)

        self.assertEqual(5, connect_mock.call_count)
        connect_mock.assert_has_calls([
            call(const.CONNECT_NOTIFY_TEXT, instance._on_change_base_entry, const.SETTING_HOST),
            call(const.CONNECT_NOTIFY_TEXT, instance._on_change_base_entry, const.SETTING_PORT),
            call(const.CONNECT_NOTIFY_ACTIVE, instance._on_change_base_switch, const.SETTING_SSL),
            call(const.CONNECT_NOTIFY_ACTIVE, instance._on_change_base_switch, const.SETTING_VERIFY_CERTIFICATE),
            call(const.CONNECT_NOTIFY_TEXT, instance._on_change_base_entry, const.SETTING_TOKEN)
        ])

        self.assertEqual(1, group_init_mock.call_count)
        self.assertEqual(6, add_mock.call_count)
        add_mock.assert_has_calls([
            call(entry_mock),
            call(entry_mock),
            call(switch_mock),
            call(switch_mock),
            call(password_entry_mock),
            call(entry_mock)
        ])

