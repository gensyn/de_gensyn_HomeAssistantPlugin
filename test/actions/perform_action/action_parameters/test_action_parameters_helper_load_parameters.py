import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.actions.perform_action import const
from de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters import action_parameters_helper


class TestActionParametersHelperLoadParameters(unittest.TestCase):

    def test_load_parameters_no_ha_entity(self):
        entity_id = "light.living_room"

        ha_entity = None
        ha_action = "turn_on"

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_not_called()
        action.parameters_expander.add_row.assert_not_called()

    def test_load_parameters_no_ha_action(self):
        entity_id = "light.living_room"

        ha_entity = Mock()
        ha_action = None

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_not_called()
        action.parameters_expander.add_row.assert_not_called()

    def test_load_parameters_no_fields(self):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = Mock()
        ha_action = "turn_on"

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: {}
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_not_called()

    def test_load_parameters_no_selector(self):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = Mock()
        ha_action = "turn_on"

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: {
                    "brightness": {
                    }
                }
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_not_called()

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.ParameterComboRow')
    def test_load_parameters_combo_row_selector(self, parameter_combo_row_mock):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = Mock()
        ha_action = "turn_on"

        fields = {
            "brightness": {
                const.NAME: "Brightness",
                const.REQUIRED: True,
                const.SELECTOR: {
                    const.SELECT: {
                        const.OPTIONS: [
                            "25%",
                            "50%",
                            "75%",
                            "100%"
                        ]
                    }
                }
            },
            const.ADVANCED_FIELDS: {
                const.ATTRIBUTE_FIELDS: {
                    "color_temp": {}
                }
            }
        }

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: fields
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.settings.get_parameters = Mock()
        action.settings.get_parameters.return_value = action.settings.get_parameters
        action.settings.get_parameters.get = Mock(return_value="75%")
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        parameter_combo_row_mock.return_value = parameter_combo_row_mock
        parameter_combo_row_mock.widget = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_called_once_with(parameter_combo_row_mock.widget)
        parameter_combo_row_mock.assert_called_once_with(action, f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.brightness", "Brightness", "75%", ["25%", "50%", "75%", "100%"], True)
        assert "color_temp" in fields
        assert const.ADVANCED_FIELDS not in fields

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.ParameterComboRow')
    def test_load_parameters_combo_row_list(self, parameter_combo_row_mock):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = {
            const.ATTRIBUTES: {
                "brightness_list": [
                    {const.VALUE: "25%"},
                    {const.VALUE: "50%"},
                    {const.VALUE: "75%"},
                    {const.VALUE: "100%"}
                ]
            }
        }
        ha_action = "turn_on"

        fields = {
            "brightness": {
                const.SELECTOR: {
                    const.NUMBER: {}
                }
            }
        }

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: fields
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.settings.get_parameters = Mock()
        action.settings.get_parameters.return_value = action.settings.get_parameters
        action.settings.get_parameters.get = Mock(return_value=None)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        parameter_combo_row_mock.return_value = parameter_combo_row_mock
        parameter_combo_row_mock.widget = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_called_once_with(parameter_combo_row_mock.widget)
        parameter_combo_row_mock.assert_called_once_with(action, f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.brightness", "brightness", const.EMPTY_STRING, ["25%", "50%", "75%", "100%"], False)

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.ParameterSwitchRow')
    def test_load_parameters_switch_row_with_value(self, parameter_switch_row_mock):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = {
            "entity_id": entity_id,
        }
        ha_action = "turn_on"

        fields = {
            "brightness": {
                const.NAME: "Brightness",
                const.REQUIRED: True,
                const.SELECTOR: {
                    const.BOOLEAN: {}
                }
            }
        }

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: fields
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.settings.get_parameters = Mock()
        action.settings.get_parameters.return_value = action.settings.get_parameters
        action.settings.get_parameters.get = Mock(return_value=True)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        parameter_switch_row_mock.return_value = parameter_switch_row_mock
        parameter_switch_row_mock.widget = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_called_once_with(parameter_switch_row_mock.widget)
        parameter_switch_row_mock.assert_called_once_with(action, f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.brightness", "Brightness", True, True)

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.ParameterSwitchRow')
    def test_load_parameters_switch_row_without_value(self, parameter_switch_row_mock):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = {
            "entity_id": entity_id,
        }
        ha_action = "turn_on"

        fields = {
            "brightness": {
                const.NAME: "Brightness",
                const.REQUIRED: True,
                const.DEFAULT: True,
                const.SELECTOR: {
                    const.BOOLEAN: {}
                }
            }
        }

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: fields
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.settings.get_parameters = Mock()
        action.settings.get_parameters.return_value = action.settings.get_parameters
        action.settings.get_parameters.get = Mock(return_value=None)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        parameter_switch_row_mock.return_value = parameter_switch_row_mock
        parameter_switch_row_mock.widget = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_called_once_with(parameter_switch_row_mock.widget)
        parameter_switch_row_mock.assert_called_once_with(action, f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.brightness", "Brightness", True, True)

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.ParameterScaleRow')
    def test_load_parameters_scale_row_with_value(self, parameter_scale_row_mock):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = {
            "entity_id": entity_id,
        }
        ha_action = "turn_on"

        fields = {
            "brightness": {
                const.NAME: "Brightness",
                const.REQUIRED: True,
                const.SELECTOR: {
                    const.NUMBER: {
                        const.MIN: 1,
                        const.MAX: 99,
                        const.STEP: 0.5
                    }
                }
            }
        }

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: fields
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.settings.get_parameters = Mock()
        action.settings.get_parameters.return_value = action.settings.get_parameters
        action.settings.get_parameters.get = Mock(return_value=48.5)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        parameter_scale_row_mock.return_value = parameter_scale_row_mock
        parameter_scale_row_mock.widget = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_called_once_with(parameter_scale_row_mock.widget)
        parameter_scale_row_mock.assert_called_once_with(action, f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.brightness", "Brightness", 48.5, 1, 99, 0.5, True)

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.ParameterScaleRow')
    def test_load_parameters_scale_row_without_value(self, parameter_scale_row_mock):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = {
            "entity_id": entity_id,
        }
        ha_action = "turn_on"

        fields = {
            "brightness": {
                const.NAME: "Brightness",
                const.REQUIRED: True,
                const.DEFAULT: 7,
                const.SELECTOR: {
                    const.NUMBER: {
                        const.MIN: 1,
                        const.MAX: 99,
                        const.STEP: 0.5
                    }
                }
            }
        }

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: fields
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.settings.get_parameters = Mock()
        action.settings.get_parameters.return_value = action.settings.get_parameters
        action.settings.get_parameters.get = Mock(return_value=None)
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        parameter_scale_row_mock.return_value = parameter_scale_row_mock
        parameter_scale_row_mock.widget = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_called_once_with(parameter_scale_row_mock.widget)
        parameter_scale_row_mock.assert_called_once_with(action, f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.brightness", "Brightness", 7, 1, 99, 0.5, True)

    @patch('de_gensyn_HomeAssistantPlugin.actions.perform_action.action_parameters.action_parameters_helper.ParameterEntryRow')
    def test_load_parameters_entry_row(self, parameter_entry_row_mock):
        domain = "light"
        entity_id = "light.living_room"

        ha_entity = {
            "entity_id": entity_id,
        }
        ha_action = "turn_on"

        fields = {
            "brightness": {
                const.NAME: "Brightness",
                const.REQUIRED: False,
                const.SELECTOR: {
                    "other": {}
                }
            }
        }

        actions = {
            ha_action: {
                const.ATTRIBUTE_FIELDS: fields
            }
        }

        action = Mock()
        action.settings = Mock()
        action.settings.get_entity = Mock(return_value=entity_id)
        action.settings.get_action = Mock(return_value=ha_action)
        action.settings.get_parameters = Mock()
        action.settings.get_parameters.return_value = action.settings.get_parameters
        action.settings.get_parameters.get = Mock(return_value="some text")
        action.parameters_expander = Mock()
        action.parameters_expander.clear_rows = Mock()
        action.parameters_expander.add_row = Mock()
        action.plugin_base = Mock()
        action.plugin_base.backend = Mock()
        action.plugin_base.backend.get_entity = Mock(return_value=ha_entity)
        action.plugin_base.backend.get_actions = Mock(return_value=actions)
        action.domain_combo = Mock()
        action.domain_combo.get_selected_item = Mock(return_value=domain)

        parameter_entry_row_mock.return_value = parameter_entry_row_mock
        parameter_entry_row_mock.widget = Mock()

        action_parameters_helper.load_parameters(action)

        action.parameters_expander.clear_rows.assert_called_once()
        action.settings.get_entity.assert_called_once()
        action.plugin_base.backend.get_entity.assert_called_once_with(entity_id)
        action.settings.get_action.assert_called_once()
        action.plugin_base.backend.get_actions.assert_called_once_with(domain)
        action.parameters_expander.add_row.assert_called_once_with(parameter_entry_row_mock.widget)
        parameter_entry_row_mock.assert_called_once_with(action, f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.brightness", "Brightness", "some text", False)


if __name__ == '__main__':
    unittest.main()
