"""
Module for service parameter operations.
"""
from typing import Dict

import gi

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper import helper
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.helper.scale_row import ScaleRow

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import CheckButton, StringList
from gi.repository.Adw import ComboRow, EntryRow, SwitchRow


def load_service_parameters(action):
    """
    Load service parameters from Home Assistant.
    """
    action.service_parameters.clear()

    ha_entity = action.plugin_base.backend.get_entity(action.settings[const.SETTING_ENTITY_ENTITY])

    service = action.settings[const.SETTING_SERVICE_SERVICE]

    if not ha_entity or not service:
        return

    fields = action.plugin_base.backend.get_services(
        action.entity_domain_combo.get_selected_item().get_string()).get(
        service, {}).get(const.ATTRIBUTE_FIELDS, {})

    fields.update(fields.get("advanced_fields", {}).get(const.ATTRIBUTE_FIELDS, {}))
    fields.pop("advanced_fields", None)

    for field in fields:
        check = CheckButton()

        setting_value = action.settings[const.SETTING_SERVICE_PARAMETERS].get(field)

        selector = list(fields[field]["selector"].keys())[0]

        if selector == "select" or f"{field}_list" in ha_entity.get(const.ATTRIBUTES,
                                                                    {}).keys():
            row = _create_combo_row(selector, fields, field, ha_entity, action, check,
                                    setting_value)
        elif selector == "boolean":
            row = _create_switch_row(fields, field, action, check, setting_value)
        elif selector == "number":
            row = _create_scale_row(fields, field, action, check, setting_value)
        else:
            row = _create_entry_row(field, action, check, setting_value)

        check.set_active(field in action.settings[const.SETTING_SERVICE_PARAMETERS].keys())
        check.connect(const.CONNECT_TOGGLED, _on_change_parameters_check, action, row, field)

        row.add_prefix(check)
        action.service_parameters.add_row(row)


def _on_change_parameters_combo(combo, *args):
    """
    Execute when a new selection is made in a combo row for a service parameter.
    """
    check = args[2]

    if not check.get_active():
        # CheckButton is not checked - don't save value
        return

    action = args[1]
    field = args[3]

    value = combo.get_selected_item().get_string()
    if value:
        action.settings[const.SETTING_SERVICE_PARAMETERS][field] = value
    else:
        action.settings[const.SETTING_SERVICE_PARAMETERS].pop(field, None)
    action.set_settings(action.settings)


def _on_change_parameters_switch(switch, *args):
    """
    Execute when a switch is changed in a combo row for a service parameter.
    """
    check = args[2]

    if not check.get_active():
        # CheckButton is not checked - don't save value
        return

    action = args[1]
    field = args[3]

    action.settings[const.SETTING_SERVICE_PARAMETERS][field] = switch.get_active()
    action.set_settings(action.settings)


def _on_change_parameters_entry(entry, *args):
    """
    Execute when the text is changed in an entry row for a service parameter.
    """
    check = args[2]

    if not check.get_active():
        # CheckButton is not checked - don't save value
        return

    action = args[1]
    field = args[3]

    value = entry.get_text()
    if value:
        action.settings[const.SETTING_SERVICE_PARAMETERS][field] = value
    else:
        action.settings[const.SETTING_SERVICE_PARAMETERS].pop(field, None)
    action.set_settings(action.settings)


def _on_change_parameters_scale(scale, *args):
    """
    Execute when the value is changed in a scale for a service parameter.
    """
    check = args[2]

    if not check.get_active():
        # CheckButton is not checked - don't save value
        return

    action = args[1]
    field = args[3]

    action.settings[const.SETTING_SERVICE_PARAMETERS][field] = int(scale.get_value())
    action.set_settings(action.settings)


def _on_change_parameters_check(check, *args):
    """
    Execute when the checkbox is toggled in a row for a service parameter.
    """
    action = args[0]
    field = args[2]

    if check.get_active():
        row = args[1]

        if isinstance(row, ComboRow):
            value = row.get_selected_item().get_string()
        elif isinstance(row, SwitchRow):
            value = row.get_active()
        elif isinstance(row, ScaleRow):
            value = row.get_value()
        else:
            value = row.get_text()

        action.settings[const.SETTING_SERVICE_PARAMETERS][field] = value
    else:
        action.settings[const.SETTING_SERVICE_PARAMETERS].pop(field, None)

    action.set_settings(action.settings)


def _create_combo_row(selector: str, fields: Dict, field: str, ha_entity, action,
                      check: CheckButton,
                      setting_value) -> ComboRow:
    if selector == "select":
        options = fields[field]["selector"]["select"]["options"]
    else:
        options = ha_entity.get(const.ATTRIBUTES, {})[f"{field}_list"]

    if not isinstance(options[0], str):
        options = [opt["value"] for opt in options]

    model = StringList.new([const.EMPTY_STRING, *options])

    row = ComboRow(title=field)
    row.set_model(model)
    row.connect(const.CONNECT_NOTIFY_SELECTED, _on_change_parameters_combo, action, check,
                field)
    row.connect(const.CONNECT_NOTIFY_SELECTED, lambda _, __: check.set_active(True))

    if setting_value:
        helper.set_value_in_combo(row, setting_value)

    return row


def _create_switch_row(fields: Dict, field: str, action, check: CheckButton,
                       setting_value) -> SwitchRow:
    value = False

    if setting_value:
        value = setting_value
    else:
        default_value = fields[field].get("default")
        if default_value:
            value = bool(default_value)

    row = SwitchRow(title=field, active=value)
    row.connect(const.CONNECT_NOTIFY_ACTIVE, _on_change_parameters_switch, action, check,
                field)
    row.connect(const.CONNECT_NOTIFY_ACTIVE, lambda _, __: check.set_active(True))

    return row


def _create_scale_row(fields: Dict, field: str, action, check: CheckButton,
                      setting_value) -> ScaleRow:
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

    row = ScaleRow(field, number_min, number_max, number_step)
    row.set_value(int(value))
    row.connect(const.CONNECT_VALUE_CHANGED, _on_change_parameters_scale, action, check,
                field)
    row.connect(const.CONNECT_VALUE_CHANGED, lambda _, __: check.set_active(True))

    return row


def _create_entry_row(field: str, action, check: CheckButton, setting_value) -> EntryRow:
    value = str(setting_value) if setting_value else const.EMPTY_STRING

    row = EntryRow(title=field, text=value)
    row.connect(const.CONNECT_NOTIFY_TEXT, _on_change_parameters_entry, action, check,
                field)
    row.connect(const.CONNECT_NOTIFY_TEXT, lambda _, __: check.set_active(True))

    value = str(setting_value) if setting_value else const.EMPTY_STRING

    row = EntryRow(title=field, text=value)
    row.connect(const.CONNECT_NOTIFY_TEXT, _on_change_parameters_entry, action, check,
                field)
    row.connect(const.CONNECT_NOTIFY_TEXT, lambda _, __: check.set_active(bool(row.get_text())))

    return row
