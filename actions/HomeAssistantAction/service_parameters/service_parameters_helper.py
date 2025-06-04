"""
Module for service parameter operations.
"""
from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.service_parameters.parameter_combo_row import \
    ParameterComboRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.service_parameters.parameter_entry_row import \
    ParameterEntryRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.service_parameters.parameter_scale_row import \
    ParameterScaleRow
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.service_parameters.parameter_switch_row import \
    ParameterSwitchRow


def load_service_parameters(action):
    """
    Load service parameters from Home Assistant.
    """
    action.service_parameters.clear_rows()

    ha_entity = action.plugin_base.backend.get_entity(action.settings.get_entity())

    service = action.settings.get_service()

    if not ha_entity or not service:
        return

    fields = action.plugin_base.backend.get_services(
        str(action.entity_domain_combo.get_selected_item())).get(
        service, {}).get(const.ATTRIBUTE_FIELDS, {})

    fields.update(fields.get("advanced_fields", {}).get(const.ATTRIBUTE_FIELDS, {}))
    fields.pop("advanced_fields", None)

    for field in fields:
        setting_value = action.settings.get_service_parameters().get(field)

        if not "selector" in fields[field]:
            continue

        selector = list(fields[field]["selector"].keys())[0]

        var_name = f"{const.SETTING_SERVICE}.{const.SETTING_PARAMETERS}.{field}"
        if selector == "select" or f"{field}_list" in ha_entity.get(const.ATTRIBUTES,
                                                                    {}).keys():
            if selector == "select":
                options = fields[field]["selector"]["select"]["options"]
            else:
                options = ha_entity.get(const.ATTRIBUTES, {})[f"{field}_list"]

            if not isinstance(options[0], str):
                options = [opt["value"] for opt in options]

            if setting_value is None:
                setting_value = const.EMPTY_STRING

            row = ParameterComboRow(action, var_name, field, setting_value, options)
        elif selector == "boolean":
            value = False

            if setting_value:
                value = setting_value
            else:
                default_value = fields[field].get("default")
                if default_value:
                    value = bool(default_value)

            row = ParameterSwitchRow(action, var_name, field, value)
        elif selector == "number":
            number_min = fields[field]["selector"]["number"]["min"]
            number_max = fields[field]["selector"]["number"]["max"]
            number_step = fields[field]["selector"]["number"].get("step", 1)

            value = number_min

            if setting_value:
                value = setting_value
            else:
                default_value = fields[field].get("default")
                if default_value:
                    value = default_value

            row = ParameterScaleRow(action, var_name, field, value, number_min, number_max, number_step)
        else:
            value = str(setting_value) if setting_value else const.EMPTY_STRING
            row = ParameterEntryRow(action, var_name, field, value)

        action.service_parameters.add_row(row.widget)
