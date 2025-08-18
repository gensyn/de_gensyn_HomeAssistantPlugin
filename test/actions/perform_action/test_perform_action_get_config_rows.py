import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from src.backend.DeckManagement.InputIdentifier import Input
from de_gensyn_HomeAssistantPlugin.actions.perform_action import const
from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionGetConfigRows(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    def test_get_config_rows_success(self, _):
        domain_combo_mock = Mock()
        domain_combo_mock.widget = "domain"

        action_combo_mock = Mock()
        action_combo_mock.widget = "action"

        entity_combo_mock = Mock()
        entity_combo_mock.widget = "entity"

        parameters_expander_mock = Mock()
        parameters_expander_mock.widget = "parameters"

        instance = PerformAction()
        instance.domain_combo = domain_combo_mock
        instance.action_combo = action_combo_mock
        instance.entity_combo = entity_combo_mock
        instance.parameters_expander = parameters_expander_mock
        result = instance.get_config_rows()

        self.assertEqual(result, [
            domain_combo_mock.widget,
            action_combo_mock.widget,
            entity_combo_mock.widget,
            parameters_expander_mock.widget
        ])


if __name__ == '__main__':
    unittest.main()
