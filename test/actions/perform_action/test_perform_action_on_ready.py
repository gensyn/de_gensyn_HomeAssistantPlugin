import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionOnReady(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.on_ready')
    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.ActionSettings')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_reload')
    def test_on_ready_not_connected(self, reload_mock, load_actions_mock, action_settings_mock, on_ready_mock, _):
        backend_mock = Mock()
        backend_mock.is_connected = Mock(return_value=False)

        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = PerformAction()
        instance.plugin_base = plugin_base_mock
        instance.on_ready()

        action_settings_mock.assert_called_once_with(instance)
        on_ready_mock.assert_called_once()
        load_actions_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.on_ready')
    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.ActionSettings')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_reload')
    def test_on_ready_success(self, reload_mock, load_actions_mock, action_settings_mock, on_ready_mock, _):
        backend_mock = Mock()
        backend_mock.is_connected = Mock(return_value=True)

        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = PerformAction()
        instance.plugin_base = plugin_base_mock
        instance.on_ready()

        action_settings_mock.assert_called_once_with(instance)
        on_ready_mock.assert_called_once()
        load_actions_mock.assert_called_once()
        reload_mock.assert_called_once()
        self.assertTrue(instance.initialized)


if __name__ == '__main__':
    unittest.main()
