import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackend(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected')
    @patch.object(HomeAssistantBackend, '_load_entities')
    def test_get_domains_entities_already_loaded(self, load_entities_mock, is_connected_mock, _):
        entities = {
            "domain1": {
                "domain1.entity1": {
                    "keys": {
                        "1.1": "1.2"
                    },
                    "subscription_id": "1.3"
                },
                "domain1.entity2": {
                    "keys": {
                        "2.1": "2.2"
                    },
                    "subscription_id": "2.3"
                }
            },
            "domain2": {
                "domain2.entity3": {
                    "keys": {
                        "3.1": "3.2"
                    },
                    "subscription_id": "3.3"
                }
            }
        }
        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._entities = entities
        result = instance.get_domains()

        is_connected_mock.assert_not_called()
        load_entities_mock.assert_not_called()
        self.assertEqual(["domain1", "domain2"], result)

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=False)
    @patch.object(HomeAssistantBackend, '_load_entities')
    def test_get_domains_entities_not_loaded_not_connected(self, load_entities_mock, is_connected_mock, _):
        entities = {}
        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._entities = entities
        result = instance.get_domains()

        is_connected_mock.assert_called_once()
        load_entities_mock.assert_not_called()
        self.assertEqual([], result)

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    @patch.object(HomeAssistantBackend, '_load_entities')
    def test_get_domains_entities_not_loaded_connected(self, load_entities_mock, is_connected_mock, _):
        entities = {
            "domain1": {
                "domain1.entity1": {
                    "keys": {
                        "1.1": "1.2"
                    },
                    "subscription_id": "1.3"
                },
                "domain1.entity2": {
                    "keys": {
                        "2.1": "2.2"
                    },
                    "subscription_id": "2.3"
                }
            },
            "domain2": {
                "domain2.entity3": {
                    "keys": {
                        "3.1": "3.2"
                    },
                    "subscription_id": "3.3"
                }
            }
        }

        load_entities_mock.side_effect = lambda: setattr(instance, '_entities', entities)

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._entities = {}
        result = instance.get_domains()

        is_connected_mock.assert_called_once()
        load_entities_mock.assert_called_once()
        self.assertEqual(["domain1", "domain2"], result)


if __name__ == '__main__':
    unittest.main()
