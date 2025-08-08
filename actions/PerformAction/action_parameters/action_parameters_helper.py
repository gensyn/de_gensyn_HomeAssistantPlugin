"""
Module for action parameter operations.
"""
from de_gensyn_HomeAssistantPlugin.actions.PerformAction import const
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.action_parameters.parameter_combo_row import \
    ParameterComboRow
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.action_parameters.parameter_entry_row import \
    ParameterEntryRow
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.action_parameters.parameter_scale_row import \
    ParameterScaleRow
from de_gensyn_HomeAssistantPlugin.actions.PerformAction.action_parameters.parameter_switch_row import \
    ParameterSwitchRow


def load_parameters(action):
    """
    Load action parameters from Home Assistant.
    """
    action.parameters_expander.clear_rows()

    ha_entity = action.plugin_base.backend.get_entity(action.settings.get_entity())

    ha_action = action.settings.get_action()

    if not ha_entity or not ha_action:
        return

    fields = action.plugin_base.backend.get_actions(
        str(action.domain_combo.get_selected_item())).get(
        ha_action, {}).get(const.ATTRIBUTE_FIELDS, {})

    fields.update(fields.get(const.ADVANCED_FIELDS, {}).get(const.ATTRIBUTE_FIELDS, {}))
    fields.pop(const.ADVANCED_FIELDS, None)

    for field_name, field_settings in fields.items():
        setting_value = action.settings.get_parameters().get(field_name)

        if not const.SELECTOR in fields[field_name]:
            continue

        selector = list(fields[field_name][const.SELECTOR].keys())[0]

        name = field_settings.get(const.NAME, field_name)
        var_name = f"{const.SETTING_SERVICE}.{const.ACTION_PARAMETERS}.{field_name}"
        required = field_settings.get(const.REQUIRED, False)
        if selector == const.SELECT or f"{field_name}{const.LIST}" in ha_entity.get(const.ATTRIBUTES,
                                                                               {}).keys():
            if selector == const.SELECT:
                options = fields[field_name][const.SELECTOR][const.SELECT][const.OPTIONS]
            else:
                options = ha_entity.get(const.ATTRIBUTES, {})[f"{field_name}{const.LIST}"]

            if not isinstance(options[0], str):
                options = [opt[const.VALUE] for opt in options]

            if setting_value is None:
                setting_value = const.EMPTY_STRING

            row = ParameterComboRow(action, var_name, name, setting_value, options, required)
        elif selector == const.BOOLEAN:
            value = False

            if setting_value:
                value = setting_value
            else:
                default_value = fields[field_name].get(const.DEFAULT)
                if default_value:
                    value = bool(default_value)

            row = ParameterSwitchRow(action, var_name, name, value, required)
        elif selector == const.NUMBER:
            number_min = fields[field_name][const.SELECTOR][const.NUMBER][const.MIN]
            number_max = fields[field_name][const.SELECTOR][const.NUMBER][const.MAX]
            number_step = fields[field_name][const.SELECTOR][const.NUMBER].get(const.STEP, 1)

            value = number_min

            if setting_value:
                value = setting_value
            else:
                default_value = fields[field_name].get(const.DEFAULT)
                if default_value:
                    value = default_value

            row = ParameterScaleRow(action, var_name, name, value, number_min, number_max, number_step, required)
        else:
            value = str(setting_value) if setting_value else const.EMPTY_STRING
            row = ParameterEntryRow(action, var_name, name, value, required)

        action.parameters_expander.add_row(row.widget)
