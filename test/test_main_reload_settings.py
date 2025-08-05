import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.main import HomeAssistant


class TestMainReloadSettings(unittest.TestCase):

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.PerformAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.ActionHolder")
    @patch("de_gensyn_HomeAssistantPlugin.main.ConnectionSettings")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantBackend")
    def test_reload_settings_success(self, backend_mock, settings_mock, _, __, ___, ____, _____):
        set_host_mock = Mock()
        set_port_mock = Mock()
        set_ssl_mock = Mock()
        set_verify_certificate_mock = Mock()
        set_token_mock = Mock()
        connect_mock = Mock()

        backend_mock.return_value = backend_mock
        backend_mock.set_host = set_host_mock
        backend_mock.set_port = set_port_mock
        backend_mock.set_ssl = set_ssl_mock
        backend_mock.set_verify_certificate = set_verify_certificate_mock
        backend_mock.set_token = set_token_mock
        backend_mock.connect = connect_mock

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
        instance.reload_settings()

        set_host_mock.assert_called_once_with(host)
        set_port_mock.assert_called_once_with(port)
        set_ssl_mock.assert_called_once_with(ssl)
        set_verify_certificate_mock.assert_called_once_with(verify_certificate)
        set_token_mock.assert_called_once_with(token)
        connect_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
