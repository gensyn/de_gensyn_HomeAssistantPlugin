import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionPerformAction(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    def test_perform_action_no_domain(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=None)
        settings_mock.get_action = Mock(return_value='test_action')
        settings_mock.get_entity = Mock()

        backend_mock = Mock()
        backend_mock.is_connected = Mock(return_value=False)
        backend_mock.perform_action = Mock()

        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = PerformAction()
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._perform_action(None)

        settings_mock.get_entity.assert_not_called()
        backend_mock.perform_action.assert_not_called()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    def test_perform_action_no_action(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value='test_domain')
        settings_mock.get_action = Mock(return_value=None)
        settings_mock.get_entity = Mock()

        backend_mock = Mock()
        backend_mock.is_connected = Mock(return_value=False)
        backend_mock.perform_action = Mock()

        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = PerformAction()
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._perform_action(None)

        settings_mock.get_entity.assert_not_called()
        backend_mock.perform_action.assert_not_called()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    def test_perform_action_success(self, _):
        parameters = {
            'param_list': json.dumps(['item1', 'item2']),
            'param_dict': json.dumps({'key1': 'value1', 'key2': 'value2'}),
            'param_string': 'test_string',
        }

        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value='test_domain')
        settings_mock.get_action = Mock(return_value='test_action')
        settings_mock.get_entity = Mock(return_value='test_entity')

        backend_mock = Mock()
        backend_mock.is_connected = Mock(return_value=False)
        backend_mock.perform_action = Mock()
        settings_mock.get_parameters = Mock(return_value=parameters)

        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = PerformAction()
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._perform_action(None)

        settings_mock.get_entity.assert_called_once()
        backend_mock.perform_action.assert_called_once_with(
            'test_domain',
            'test_action',
            'test_entity',
            {
                'param_list': ['item1', 'item2'],
                'param_dict': {'key1': 'value1', 'key2': 'value2'},
                'param_string': 'test_string'
            }
        )


if __name__ == '__main__':
    unittest.main()
