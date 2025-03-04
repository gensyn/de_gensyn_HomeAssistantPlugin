"""
Module for service parameter operations.
"""
import gi

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import helper

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Gtk import StringList, CheckButton, EventControllerFocus
from gi.repository.Adw import ComboRow, EntryRow, SpinRow, SwitchRow


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

            if setting_value:
                helper.set_value_in_combo(row, model, setting_value)
        elif selector == "boolean":
            row = SwitchRow(title=field)
            row.connect(const.CONNECT_NOTIFY_ACTIVE, _on_change_parameters_switch, action, check,
                        field)

            if setting_value:
                row.set_active(bool(setting_value))
            else:
                default_value = fields[field].get("default")
                if default_value:
                    row.set_active(bool(default_value))
        elif selector == "number":
            number_min = fields[field]["selector"]["number"]["min"]
            number_max = fields[field]["selector"]["number"]["max"]
            number_step = fields[field]["selector"]["number"].get("step", 1)

            row = SpinRow.new_with_range(number_min, number_max, number_step)
            row.set_title(field)
            row.connect(const.CONNECT_CHANGED, _on_change_parameters_spin, action, check, field)

            focus_controller = EventControllerFocus()
            focus_controller.connect(const.CONNECT_LEAVE,
                                     _on_change_parameters_spin_event_controller, action, check,
                                     row, field)
            row.add_controller(focus_controller)

            if setting_value:
                row.set_value(setting_value)
            else:
                default_value = fields[field].get("default")
                if default_value:
                    row.set_value(default_value)
        else:
            row = EntryRow(title=field)
            row.connect(const.CONNECT_NOTIFY_TEXT, _on_change_parameters_entry, action, check,
                        field)

            if setting_value:
                row.set_text(str(setting_value))

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


def _on_change_parameters_spin(spin, *args):
    """
    Execute when the number is changed in a spin row for a service parameter.
    """
    check = args[1]

    if not check.get_active():
        # CheckButton is not checked - don't save value
        return

    action = args[0]
    field = args[2]

    action.settings[const.SETTING_SERVICE_PARAMETERS][field] = spin.get_value()
    action.set_settings(action.settings)


def _on_change_parameters_spin_event_controller(_, *args):
    """
    Execute when a spin row for a service parameter loses focus.
    """
    check = args[1]

    if not check.get_active():
        # CheckButton is not checked - don't save value
        return

    action = args[0]
    row = args[2]
    field = args[3]

    action.settings[const.SETTING_SERVICE_PARAMETERS][field] = row.get_value()
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
        elif isinstance(row, SpinRow):
            value = row.get_value()
        else:
            value = row.get_text()

        action.settings[const.SETTING_SERVICE_PARAMETERS][field] = value
    else:
        action.settings[const.SETTING_SERVICE_PARAMETERS].pop(field, None)

    action.set_settings(action.settings)
