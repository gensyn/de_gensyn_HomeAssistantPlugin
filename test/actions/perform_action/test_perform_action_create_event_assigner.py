import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from src.backend.DeckManagement.InputIdentifier import Input
from de_gensyn_HomeAssistantPlugin.actions.perform_action import perform_const
from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionCreateEventAssigner(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.EventAssigner')
    @patch.object(PerformAction, 'add_event_assigner')
    def test_create_event_assigner_success(self, add_event_assigner_mock, event_assigner_mock, _):
        instance = PerformAction()
        instance._create_event_assigner()

        add_event_assigner_mock.assert_called_once_with(event_assigner_mock.return_value)
        event_assigner_mock.assert_called_once_with(id=perform_const.ACTION_ID, ui_label=perform_const.ACTION_NAME,
                                                    default_events=[Input.Key.Events.DOWN],
                                                    callback=instance._perform_action)


if __name__ == '__main__':
    unittest.main()
