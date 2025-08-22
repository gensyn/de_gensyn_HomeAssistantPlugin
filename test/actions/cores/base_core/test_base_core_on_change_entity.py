import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreOnChangeDomain(unittest.TestCase):

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_set_enabled_disabled")
    def test_on_change_entity_no_old_entity(self, set_enabled_disabled_mock, _, __):
        old_entity_id = None
        new_entity_id = "switch.kitchen"

        instance = BaseCore(True)
        instance.initialized = True
        instance._on_change_entity(None, new_entity_id, old_entity_id)

        instance.plugin_base.backend.remove_tracked_entity.assert_not_called()
        instance.plugin_base.backend.add_tracked_entity.assert_called_once_with(new_entity_id, instance.refresh)
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_set_enabled_disabled")
    def test_on_change_entity_no_new_entity(self, set_enabled_disabled_mock, _, __):
        old_entity_id = "light.living_room"
        new_entity_id = None

        instance = BaseCore(True)
        instance.initialized = True
        instance._on_change_entity(None, new_entity_id, old_entity_id)

        instance.plugin_base.backend.remove_tracked_entity.assert_called_once_with(old_entity_id,
                                                                                   instance.refresh)
        instance.plugin_base.backend.add_tracked_entity.assert_not_called()
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_set_enabled_disabled")
    def test_on_change_entity_entity_not_tracked(self, set_enabled_disabled_mock, _, __):
        old_entity_id = "light.living_room"
        new_entity_id = "switch.kitchen"

        instance = BaseCore(False)
        instance.initialized = True
        instance._on_change_entity(None, new_entity_id, old_entity_id)

        instance.plugin_base.backend.remove_tracked_entity.assert_not_called()
        instance.plugin_base.backend.add_tracked_entity.assert_not_called()
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_set_enabled_disabled")
    def test_on_change_entity_success(self, set_enabled_disabled_mock, _, __):
        old_entity_id = "light.living_room"
        new_entity_id = "switch.kitchen"

        instance = BaseCore(True)
        instance.initialized = True
        instance._on_change_entity(None, new_entity_id, old_entity_id)

        instance.plugin_base.backend.remove_tracked_entity.assert_called_once_with(old_entity_id,
                                                                                   instance.refresh)
        instance.plugin_base.backend.add_tracked_entity.assert_called_once_with(new_entity_id, instance.refresh)
        set_enabled_disabled_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
