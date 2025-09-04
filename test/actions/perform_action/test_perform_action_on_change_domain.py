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

    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core.log.info')
    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore._on_change_domain')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_set_enabled_disabled')
    def test_on_change_domain_not_initialized(self, set_enabled_disabled_mock, load_actions_mock, on_change_domain_mock,
                                              _, __):
        new_domain = 'light'
        old_domain = 'switch'

        instance = PerformAction()
        instance.initialized = False
        instance._on_change_domain(None, new_domain, old_domain)

        on_change_domain_mock.assert_not_called()
        load_actions_mock.assert_not_called()
        set_enabled_disabled_mock.assert_not_called()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore._on_change_domain')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_set_enabled_disabled')
    def test_on_change_domain_domain_none(self, set_enabled_disabled_mock, load_actions_mock, on_change_domain_mock,
                                          _):
        new_domain = None
        old_domain = 'switch'

        instance = PerformAction()
        instance.initialized = True
        instance._on_change_domain(None, new_domain, old_domain)

        on_change_domain_mock.assert_called_once_with(None, new_domain, old_domain)
        load_actions_mock.assert_not_called()
        set_enabled_disabled_mock.assert_called_once()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore._on_change_domain')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_set_enabled_disabled')
    def test_on_change_domain_domain_empty(self, set_enabled_disabled_mock, load_actions_mock, on_change_domain_mock,
                                           _):
        new_domain = ""
        old_domain = 'switch'

        instance = PerformAction()
        instance.initialized = True
        instance._on_change_domain(None, new_domain, old_domain)

        on_change_domain_mock.assert_called_once_with(None, new_domain, old_domain)
        load_actions_mock.assert_not_called()
        set_enabled_disabled_mock.assert_called_once()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'de_gensyn_HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore._on_change_domain')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_set_enabled_disabled')
    def test_on_change_domain_success(self, set_enabled_disabled_mock, load_actions_mock, on_change_domain_mock,
                                      _):
        new_domain = "light"
        old_domain = 'switch'

        instance = PerformAction()
        instance.initialized = True
        instance._on_change_domain(None, new_domain, old_domain)

        on_change_domain_mock.assert_called_once_with(None, new_domain, old_domain)
        load_actions_mock.assert_called_once()
        set_enabled_disabled_mock.assert_called_once()

