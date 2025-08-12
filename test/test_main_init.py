import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.main import HomeAssistant
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.const import HOME_ASSISTANT_ACTION
from de_gensyn_HomeAssistantPlugin.actions.perform_action.const import PERFORM_ACTION


class TestMainInit(unittest.TestCase):

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("de_gensyn_HomeAssistantPlugin.main.ConnectionSettings")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantBackend")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.PerformAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.ActionHolder")
    def test_init_success(self, action_holder_mock, perform_action_mock, ha_action_mock, backend_mock, settings_mock,
                  register_mock, add_action_holder_mock):
        action_holder_mock.side_effect = [ha_action_mock, perform_action_mock]

        host: str = "localhost"
        port: str = "8123"
        ssl: bool = True
        verify_certificate: bool = False
        token: str = "abc"

        settings_mock.return_value = settings_mock
        settings_mock.get_host = lambda: host
        settings_mock.get_port = lambda: port
        settings_mock.get_ssl = lambda: ssl
        settings_mock.get_verify_certificate = lambda: verify_certificate
        settings_mock.get_token = lambda: token

        instance = HomeAssistant()

        self.assertIsNone(instance.host_entry)
        self.assertIsNone(instance.port_entry)
        self.assertIsNone(instance.ssl_switch)
        self.assertIsNone(instance.verify_certificate_switch)
        self.assertIsNone(instance.token_entry)

        self.assertEqual(2, action_holder_mock.call_count)
        action_holder_mock.assert_has_calls([
            call(
                plugin_base=instance,
                action_base=ha_action_mock,
                action_id="de_gensyn_HomeAssistantPlugin::HomeAssistantAction",
                action_name=HOME_ASSISTANT_ACTION
            ),
            call(
                plugin_base=instance,
                action_base=perform_action_mock,
                action_id="de_gensyn_HomeAssistantPlugin::PerformAction",
                action_name=PERFORM_ACTION
            )
        ])

        self.assertEqual(2, add_action_holder_mock.call_count)
        add_action_holder_mock.assert_has_calls([
            call(ha_action_mock),
            call(perform_action_mock)
        ])

        self.assertEqual(1, register_mock.call_count)
        register_mock.assert_called_once_with(
            plugin_name=const.HOME_ASSISTANT,
            github_repo="https://github.com/gensyn/de_gensyn_HomeAssistantPlugin",
            plugin_version="1.0.3",
            app_version="1.5.0-beta"
        )

        settings_mock.assert_called_once_with(instance)

        backend_mock.assert_called_once_with(host, port, ssl, verify_certificate, token)


if __name__ == '__main__':
    unittest.main()
