import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionGetDomains(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    def test_get_domains_success(self, _):
        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_domains_for_actions = Mock(return_value=['light', 'switch', 'media_player'])

        instance = PerformAction()
        instance.plugin_base = plugin_base_mock
        result = instance._get_domains()

        self.assertEqual(result, ['light', 'switch', 'media_player'])
        plugin_base_mock.backend.get_domains_for_actions.assert_called_once()


if __name__ == '__main__':
    unittest.main()
