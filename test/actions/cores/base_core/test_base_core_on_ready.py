import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreOnReady(unittest.TestCase):

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_domains")
    @patch.object(BaseCore, "_load_entities")
    def test_on_read_no_entity(self, load_entities_mock, load_domains_mock, _, __):
        track_entity = True

        settings_implementation = Mock()
        settings_implementation.return_value = settings_implementation
        settings_implementation.get_entity.return_value = None

        instance = BaseCore(settings_implementation, track_entity)
        instance.on_ready()

        instance.plugin_base.backend.add_action_ready_callback.assert_called_once_with(instance.on_ready)
        settings_implementation.get_entity.assert_called_once()
        instance.plugin_base.backend.add_tracked_entity.assert_not_called()
        load_entities_mock.assert_called_once()
        load_domains_mock.assert_called_once()

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_domains")
    @patch.object(BaseCore, "_load_entities")
    def test_on_read_entity_not_tracked(self, load_entities_mock, load_domains_mock, _, __):
        track_entity = False

        settings_implementation = Mock()
        settings_implementation.return_value = settings_implementation
        settings_implementation.get_entity.return_value = "entity"

        instance = BaseCore(settings_implementation, track_entity)
        instance.on_ready()

        instance.plugin_base.backend.add_action_ready_callback.assert_called_once_with(instance.on_ready)
        settings_implementation.get_entity.assert_called_once()
        instance.plugin_base.backend.add_tracked_entity.assert_not_called()
        load_entities_mock.assert_called_once()
        load_domains_mock.assert_called_once()

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_domains")
    @patch.object(BaseCore, "_load_entities")
    def test_on_read_success(self, load_entities_mock, load_domains_mock, _, __):
        track_entity = True

        settings_implementation = Mock()
        settings_implementation.return_value = settings_implementation
        settings_implementation.get_entity.return_value = "entity"

        instance = BaseCore(settings_implementation, track_entity)
        instance.on_ready()

        instance.plugin_base.backend.add_action_ready_callback.assert_called_once_with(instance.on_ready)
        settings_implementation.get_entity.assert_called_once()
        instance.plugin_base.backend.add_tracked_entity.assert_called_once_with("entity", instance.refresh)
        load_entities_mock.assert_called_once()
        load_domains_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
