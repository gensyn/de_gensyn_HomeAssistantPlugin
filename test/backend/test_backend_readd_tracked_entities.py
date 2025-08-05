import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackendReaddTrackedEntities(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'add_tracked_entity')
    def test_readd_tracked_entities_no_entities(self, add_tracked_entity_mock, _):
        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._readd_tracked_entities()

        add_tracked_entity_mock.assert_not_called()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'add_tracked_entity')
    def test_readd_tracked_entities_success(self, add_tracked_entity_mock, _):
        entities = {
            "domain1": {
                "domain1.entity1": {
                    const.ACTIONS: {
                        "1.1"
                    },
                    const.SUBSCRIPTION_ID: "1.3"
                },
                "domain1.entity2": {
                    const.ACTIONS: set(),
                    const.SUBSCRIPTION_ID: "2.3"
                }
            },
            "domain2": {
                "domain2.entity3": {
                    const.ACTIONS: {
                        "3.1"
                    },
                    const.SUBSCRIPTION_ID: "3.3"
                }
            }
        }

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._entities = entities
        instance._readd_tracked_entities()

        self.assertEqual(2, add_tracked_entity_mock.call_count)
        add_tracked_entity_mock.assert_has_calls(
            [call("domain1.entity1", "1.1"), call("domain2.entity3", "3.1")])
        self.assertEqual(-1, entities["domain1"]["domain1.entity1"][const.SUBSCRIPTION_ID])
        self.assertEqual("2.3", entities["domain1"]["domain1.entity2"][const.SUBSCRIPTION_ID])
        self.assertEqual(-1, entities["domain2"]["domain2.entity3"][const.SUBSCRIPTION_ID])
        self.assertEqual(set(), entities["domain1"]["domain1.entity1"][const.ACTIONS])
        self.assertEqual(set(), entities["domain1"]["domain1.entity2"][const.ACTIONS])
        self.assertEqual(set(), entities["domain2"]["domain2.entity3"][const.ACTIONS])


if __name__ == '__main__':
    unittest.main()
