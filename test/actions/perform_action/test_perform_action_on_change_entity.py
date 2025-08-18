import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionOnChangeDomain(unittest.TestCase):

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore._on_change_entity')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_not_initialized(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = 'light.kitchen'
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = False
        instance._on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_not_called()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore._on_change_entity')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_same_entity(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = 'light.kitchen'
        old_entity = 'light.kitchen'

        instance = PerformAction()
        instance.initialized = True
        instance._on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_not_called()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore._on_change_entity')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_entity_none(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = None
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = True
        instance._on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_called_once()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_called_once()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore._on_change_entity')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_entity_empty(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = ""
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = True
        instance._on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_called_once()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_called_once()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.HomeAssistantActionCore._on_change_entity')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_success(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = 'light.kitchen'
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = True
        instance._on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_called_once()
        load_parameters_mock.assert_called_once_with(instance)
        reload_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
