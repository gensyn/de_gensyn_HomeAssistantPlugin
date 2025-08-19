import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions import const
from de_gensyn_HomeAssistantPlugin.actions.settings.settings import Settings
from de_gensyn_HomeAssistantPlugin.actions.settings.settings import DEFAULT_SETTINGS


class TestPerformActionSettingsInit(unittest.TestCase):

    @patch.object(Settings, 'load')
    def test_init_with_default(self, load_mock):
        settings = {
            "other_setting": {
                "key": "value",
            },
        }

        action_mock = Mock()
        action_mock.get_settings.return_value = settings

        settings_expected = deepcopy(settings)
        settings_expected[const.SETTING_ENTITY] = deepcopy(DEFAULT_SETTINGS)

        instance = Settings(action_mock)

        self.assertEqual(settings_expected, instance._settings)
        action_mock.set_settings.assert_called_once_with(settings_expected)
        load_mock.assert_called_once()

    def test_perform_action_settings_success(self):
        domain = "light"
        entity = "light.kitchen"

        settings = {
            const.SETTING_ENTITY: {
                const.SETTING_DOMAIN: domain,
                const.SETTING_ENTITY: entity
            },
        }

        action_mock = Mock()
        action_mock.get_settings.return_value = {}

        settings_expected = deepcopy(settings)
        settings_expected[const.SETTING_ENTITY] = deepcopy(DEFAULT_SETTINGS)

        # test init
        with patch.object(Settings, "load") as load_mock:
            instance = Settings(action_mock)
            load_mock.assert_called_once()

        self.assertEqual(settings_expected, instance._settings)
        action_mock.get_settings.assert_called_once()
        action_mock.set_settings.assert_called_once_with(settings_expected)

        # test load
        action_mock.reset_mock()
        action_mock.get_settings.return_value = settings

        instance.load()

        action_mock.get_settings.assert_called_once()
        self.assertEqual(domain, instance._domain)
        self.assertEqual(entity, instance._entity)

        # test get_domain
        self.assertEqual(domain, instance.get_domain())

        # test get_entity
        self.assertEqual(entity, instance.get_entity())

        # test reset
        settings_expected_for_reset = {
            const.SETTING_ENTITY: {
                const.SETTING_DOMAIN: "switch",
                const.SETTING_ENTITY: const.EMPTY_STRING
            }
        }

        with patch.object(Settings, "load") as load_mock:
            instance.reset("switch")
            load_mock.assert_called_once()

        self.assertEqual(settings_expected_for_reset, instance._settings)
        action_mock.set_settings.assert_called_once_with(settings_expected_for_reset)


if __name__ == '__main__':
    unittest.main()
