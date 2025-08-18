import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionOnChangeAction(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.load_parameters')
    def test_load_actions_action_in_actions(self, load_parameters_mock, _):
        settings_mock = Mock()
        settings_mock.get_action = Mock(return_value='test_action')

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value='test_domain')

        action_combo_mock = Mock()
        action_combo_mock.populate = Mock()

        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_actions = Mock(return_value={'test_action': {}, 'another_action': {}})

        instance = PerformAction()
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance.domain_combo = domain_combo_mock
        instance.action_combo = action_combo_mock
        instance._load_actions()

        settings_mock.get_action.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        plugin_base_mock.backend.get_actions.assert_called_once_with(domain_combo_mock.get_selected_item.return_value)
        action_combo_mock.populate.assert_called_once_with(
            ['test_action', 'another_action'],
            'test_action',
            update_settings=True,
            trigger_callback=False
        )
        load_parameters_mock.assert_called_once_with(instance)

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.load_parameters')
    def test_load_actions_action_not_in_actions(self, load_parameters_mock, _):
        settings_mock = Mock()
        settings_mock.get_action = Mock(return_value='test_action')

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value='test_domain')

        action_combo_mock = Mock()
        action_combo_mock.populate = Mock()

        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_actions = Mock(return_value={'one_action': {}, 'another_action': {}})

        instance = PerformAction()
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance.domain_combo = domain_combo_mock
        instance.action_combo = action_combo_mock
        instance._load_actions()

        settings_mock.get_action.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        plugin_base_mock.backend.get_actions.assert_called_once_with(domain_combo_mock.get_selected_item.return_value)
        action_combo_mock.populate.assert_called_once_with(
            ['one_action', 'another_action', 'test_action'],
            'test_action',
            update_settings=True,
            trigger_callback=False
        )
        load_parameters_mock.assert_called_once_with(instance)


if __name__ == '__main__':
    unittest.main()
