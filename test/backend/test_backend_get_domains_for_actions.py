import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendGetDomains(unittest.TestCase):

    actions = {
        "domain1": {
            "actions1": {
                "fields": {
                    "1.1": "1.2"
                }
            },
            "action2": {
                "fields": {
                    "2.1": "2.2"
                }
            }
        },
        "domain2": {
            "action3": {
                "fields": {
                    "3.1": "3.2"
                }
            }
        }
    }

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected')
    @patch.object(HomeAssistantBackend, '_load_actions')
    def test_get_domains_for_actions_entities_already_loaded(self, load_actions_mock, is_connected_mock, _):
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._actions = self.actions
        result = instance.get_domains_for_actions()

        is_connected_mock.assert_not_called()
        load_actions_mock.assert_not_called()
        self.assertEqual(["domain1", "domain2"], result)

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=False)
    @patch.object(HomeAssistantBackend, '_load_actions')
    def test_get_domains_for_actions_entities_not_loaded_not_connected(self, load_actions_mock, is_connected_mock, _):
        actions = {}
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._actions = actions
        result = instance.get_domains_for_actions()

        is_connected_mock.assert_called_once()
        load_actions_mock.assert_not_called()
        self.assertEqual([], result)

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    @patch.object(HomeAssistantBackend, '_load_actions')
    def test_get_domains_for_actions_entities_not_loaded_connected(self, load_actions_mock, is_connected_mock, _):
        load_actions_mock.side_effect = lambda: setattr(instance, '_actions', self.actions)

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = {}
        result = instance.get_domains_for_actions()

        is_connected_mock.assert_called_once()
        load_actions_mock.assert_called_once()
        self.assertEqual(["domain1", "domain2"], result)

