import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.main import HomeAssistant


class TestMainSetStatus(unittest.TestCase):

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.PerformAction")
    @patch("de_gensyn_HomeAssistantPlugin.main.ActionHolder")
    @patch("de_gensyn_HomeAssistantPlugin.main.HomeAssistantBackend")
    @patch("de_gensyn_HomeAssistantPlugin.main.ConnectionSettings")
    @patch("de_gensyn_HomeAssistantPlugin.main.GLib")
    def test_set_status(self, glib_mock, _, __, ___, ____, _____, ______, _______):
        idle_add_mock = Mock()

        glib_mock.idle_add = idle_add_mock

        set_text_mock = Mock()

        connection_status_mock = Mock()
        connection_status_mock.set_text = set_text_mock

        instance = HomeAssistant()
        instance.connection_status = connection_status_mock
        instance.set_status(const.HOME_ASSISTANT)

        idle_add_mock.assert_called_once_with(set_text_mock, const.HOME_ASSISTANT)


if __name__ == '__main__':
    unittest.main()
