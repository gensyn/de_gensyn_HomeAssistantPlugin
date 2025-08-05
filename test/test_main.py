import sys
import unittest
from pathlib import Path

from const import SETTING_HOST, SETTING_PORT, SETTING_SSL, SETTING_TOKEN, SETTING_VERIFY_CERTIFICATE

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.main import HomeAssistant


class TestMain(unittest.TestCase):

    def test_main(self):
        # test init
        instance = HomeAssistant()
        self.assertIsNotNone(instance)

        action_holder = instance.home_assistant_action_holder
        self.assertIsNotNone(action_holder)

        # without token - otherwise it tries to connect to HA
        self.assertEqual("localhost", instance.backend._host)
        self.assertEqual(8123, instance.backend._port)
        self.assertEqual(True, instance.backend._ssl)
        self.assertEqual(True, instance.backend._verify_certificate)
        self.assertEqual("", instance.backend._token)

        # test set_settings
        instance.connection.set_setting(SETTING_HOST, "hostlocal")
        instance.connection.set_setting(SETTING_PORT, 3218)
        instance.connection.set_setting(SETTING_SSL, False)
        instance.connection.set_setting(SETTING_VERIFY_CERTIFICATE, False)
        instance.connection.set_setting(SETTING_TOKEN, "")

        self.assertEqual("hostlocal", instance.get_settings().get(SETTING_HOST))
        self.assertEqual(3218, instance.get_settings().get(SETTING_PORT))
        self.assertEqual(False, instance.get_settings().get(SETTING_SSL))
        self.assertEqual(False, instance.get_settings().get(SETTING_VERIFY_CERTIFICATE))
        self.assertEqual("", instance.get_settings().get(SETTING_TOKEN))

        self.assertEqual("hostlocal", instance.backend._host)
        self.assertEqual(3218, instance.backend._port)
        self.assertEqual(False, instance.backend._ssl)
        self.assertEqual(False, instance.backend._verify_certificate)
        self.assertEqual("", instance.backend._token)

if __name__ == '__main__':
    unittest.main()
