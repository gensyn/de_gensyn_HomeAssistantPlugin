import sys
import unittest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackend(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_get_entity_no_id(self, is_connected_mock, _):
        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        result = instance.get_entity(const.EMPTY_STRING)

        expected = {
            const.STATE: const.NA,
            const.ATTRIBUTES: {},
            const.HA_CONNECTED: True
        }

        self.assertEqual(expected, result)
        is_connected_mock.assert_called_once()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_get_entity_no_dot_in_id(self, is_connected_mock, _):
        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        result = instance.get_entity("domainentitiy")

        expected = {
            const.STATE: const.NA,
            const.ATTRIBUTES: {},
            const.HA_CONNECTED: True
        }

        self.assertEqual(expected, result)
        is_connected_mock.assert_called_once()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_get_entity_success(self, is_connected_mock, _):
        entities: Dict[str, Dict[str, Any]] = {
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
                    "subscription_id": "2.3",
                    "state": "on",
                    "attributes": {
                        "brightness": 100,
                    }
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
        result = instance.get_entity("domain1.entity2")

        expected = entities["domain1"]["domain1.entity2"]
        expected[const.HA_CONNECTED] = True

        self.assertEqual(expected, result)
        self.assertEqual(2, is_connected_mock.call_count)


if __name__ == '__main__':
    unittest.main()
