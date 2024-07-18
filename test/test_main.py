import sys
import unittest
from pathlib import Path

from const import SETTING_HOST, SETTING_PORT, SETTING_SSL, SETTING_TOKEN

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")

sys.path.insert(0, absolute_mock_path)
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.main import HomeAssistant


class TestMain(unittest.TestCase):

    def test_main(self):
        # test init
        test_instance = HomeAssistant()
        self.assertIsNotNone(test_instance)

        action_holder = test_instance.home_assistant_action_holder
        self.assertIsNotNone(action_holder)

        # without token - otherwise it tries to connect to HA
        self.assertEqual("localhost", test_instance.backend._host)
        self.assertEqual(8123, test_instance.backend._port)
        self.assertEqual(True, test_instance.backend._ssl)
        self.assertEqual("", test_instance.backend._token)

        # test set_settings
        test_instance.set_settings({
            SETTING_HOST: "hostlocal",
            SETTING_PORT: 3218,
            SETTING_SSL: False,
            SETTING_TOKEN: "",
        })

        self.assertEqual("hostlocal", test_instance.get_settings().get(SETTING_HOST))
        self.assertEqual(3218, test_instance.get_settings().get(SETTING_PORT))
        self.assertEqual(False, test_instance.get_settings().get(SETTING_SSL))
        self.assertEqual("", test_instance.get_settings().get(SETTING_TOKEN))

        self.assertEqual("hostlocal", test_instance.backend._host)
        self.assertEqual(3218, test_instance.backend._port)
        self.assertEqual(False, test_instance.backend._ssl)
        self.assertEqual("", test_instance.backend._token)

        # now test token
        test_instance.set_settings({
            SETTING_HOST: "",
            SETTING_PORT: 3218,
            SETTING_SSL: False,
            SETTING_TOKEN: "cba",
        })

        self.assertEqual("", test_instance.get_settings().get(SETTING_HOST))
        self.assertEqual(3218, test_instance.get_settings().get(SETTING_PORT))
        self.assertEqual(False, test_instance.get_settings().get(SETTING_SSL))
        self.assertEqual("cba", test_instance.get_settings().get(SETTING_TOKEN))

        self.assertEqual("", test_instance.backend._host)
        self.assertEqual(3218, test_instance.backend._port)
        self.assertEqual(False, test_instance.backend._ssl)
        self.assertEqual("cba", test_instance.backend._token)


class HomeAssistantBackendMock:

    def __init__(self):
        pass


if __name__ == '__main__':
    unittest.main()
