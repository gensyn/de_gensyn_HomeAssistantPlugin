import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions import const
from de_gensyn_HomeAssistantPlugin.actions.home_assistant_action_core import HomeAssistantActionCore


class TestHomeAssistantActionCoreCreateUiElements(unittest.TestCase):

    @patch.object(HomeAssistantActionCore, "_create_event_assigner")
    def test_create_ui_elements_success(self, _):
        with patch.object(HomeAssistantActionCore, "_create_ui_elements"):
            # _create_ui_elements is called in the constructor
            instance = HomeAssistantActionCore(False)

        instance._create_ui_elements()

        self.assertEqual((instance, const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING, [],
                          const.LABEL_ENTITY_DOMAIN), instance.domain_combo.args)
        self.assertEqual({"enable_search": True,
                          "on_change": instance._on_change_domain, "can_reset": False,
                          "complex_var_name": True}, instance.domain_combo.kwargs)

        self.assertEqual((instance, const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING, [],
                          const.LABEL_ENTITY_ENTITY), instance.entity_combo.args)
        self.assertEqual({"enable_search": True,
                          "on_change": instance._on_change_entity, "can_reset": False,
                          "complex_var_name": True}, instance.entity_combo.kwargs)


if __name__ == '__main__':
    unittest.main()
