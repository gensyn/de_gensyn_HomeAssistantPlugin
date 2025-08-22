import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreLoadEntities(unittest.TestCase):

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_load_entities_entity_not_in_entities(self, _, __):
        domain = "light"
        entities = ["light.kitchen", "light.bedroom"]
        entity = "light.living_room"
        entities_sorted = sorted(entities + [entity])

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=entity)

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value=domain)

        entity_combo_mock = Mock()
        entity_combo_mock.populate = Mock()

        instance = BaseCore(True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.domain_combo = domain_combo_mock
        instance.entity_combo = entity_combo_mock
        instance.plugin_base.backend.get_entities.return_value = entities
        assert entity not in entities
        instance._load_entities()

        settings_mock.get_entity.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        instance.plugin_base.backend.get_entities.assert_called_once_with(domain)
        entity_combo_mock.populate.assert_called_once_with(entities_sorted, entity, trigger_callback=False)

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_load_entities_success(self, _, __):
        domain = "light"
        entities = ["light.living_room", "light.kitchen", "light.bedroom"]
        entities_sorted = sorted(entities)
        entity = "light.living_room"

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=entity)

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value=domain)

        entity_combo_mock = Mock()
        entity_combo_mock.populate = Mock()

        instance = BaseCore(True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.domain_combo = domain_combo_mock
        instance.entity_combo = entity_combo_mock
        instance.plugin_base.backend.get_entities.return_value = entities
        instance._load_entities()

        settings_mock.get_entity.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        instance.plugin_base.backend.get_entities.assert_called_once_with(domain)
        entity_combo_mock.populate.assert_called_once_with(entities_sorted, entity, trigger_callback=False)


if __name__ == '__main__':
    unittest.main()
