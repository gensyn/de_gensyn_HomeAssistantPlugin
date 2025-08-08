import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call, Mock

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.connection_settings.connection_settings import ConnectionSettings


class TestConnectionSettings(unittest.TestCase):

    def test_init_success(self):
        host = "localhost"
        port = "8123"
        ssl = True
        verify_certificate = False
        token = "abc"

        settings = {
            "host": host,
            "port": port,
            "ssl": ssl,
            "verify_certificate": verify_certificate,
            "token": token
        }

        get_settings_mock = Mock()
        get_settings_mock.return_value = settings

        reload_settings_mock = Mock()

        set_settings_mock = Mock()

        hass_mock = Mock()
        hass_mock.get_settings = get_settings_mock
        hass_mock.reload_settings = reload_settings_mock
        hass_mock.set_settings = set_settings_mock

        instance = ConnectionSettings(hass_mock)

        get_settings_mock.assert_called_once()
        self.assertEqual(settings, instance._settings)
        self.assertEqual(host, instance.get_host())
        self.assertEqual(port, instance.get_port())
        self.assertEqual(ssl, instance.get_ssl())
        self.assertEqual(verify_certificate, instance.get_verify_certificate())
        self.assertEqual(token, instance.get_token())

        new_host = "new_host"

        new_settings = {
            "host": new_host,
            "port": port,
            "ssl": ssl,
            "verify_certificate": verify_certificate,
            "token": token
        }

        instance.set_setting("host", new_host)

        self.assertEqual(new_host, instance.get_host())
        self.assertEqual(new_host, instance._settings.get("host"))
        reload_settings_mock.assert_called_once()
        set_settings_mock.assert_called_once_with(new_settings)


if __name__ == '__main__':
    unittest.main()
