import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.main import HomeAssistant


class TestMainOnChangeBaseEntry(unittest.TestCase):

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.PerformAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.ActionHolder")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantBackend")
    @patch("de_gensyn_HomeAssistantPlugin.main.ConnectionSettings")
    def test_on_change_base_entry_success(self, settings_mock, _, __, ___, ____, _____, ______):
        set_setting_mock = Mock()

        settings_mock.return_value = settings_mock
        settings_mock.set_setting = set_setting_mock

        entry = "host"

        test_text = "test_value"

        entry_mock = Mock()
        entry_mock.get_text = lambda: test_text

        instance = HomeAssistant()
        instance._on_change_base_entry(entry_mock, None, entry)

        set_setting_mock.assert_called_once_with(entry, test_text)

