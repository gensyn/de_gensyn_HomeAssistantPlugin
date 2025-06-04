"""
The module for settings control.
"""
import copy
import uuid
from typing import Dict, Any

from de_gensyn_HomeAssistantPlugin import const

CUSTOM_ICON = {
    const.CUSTOM_CONDITION: {
        const.CUSTOM_ATTRIBUTE: None,
        const.CUSTOM_OPERATOR: None,
        const.CUSTOM_VALUE: None
    },
    const.CUSTOM_ICON_ICON: None,
    const.CUSTOM_ICON_COLOR: None,
    const.CUSTOM_ICON_SCALE: None,
    const.CUSTOM_ICON_OPACITY: None
}

CUSTOM_TEXT = {
    const.CUSTOM_CONDITION: {
        const.CUSTOM_ATTRIBUTE: None,
        const.CUSTOM_OPERATOR: None,
        const.CUSTOM_VALUE: None
    },
    const.CUSTOM_TEXT_POSITION: None,
    const.CUSTOM_TEXT_ATTRIBUTE: None,
    const.CUSTOM_TEXT_CUSTOM_TEXT: None,
    const.CUSTOM_TEXT_ROUND: None,
    const.CUSTOM_TEXT_ROUND_PRECISION: None,
    const.CUSTOM_TEXT_TEXT_SIZE: None,
    const.CUSTOM_TEXT_TEXT_COLOR: None,
    const.CUSTOM_TEXT_OUTLINE_SIZE: None,
    const.CUSTOM_TEXT_OUTLINE_COLOR: None,
    const.CUSTOM_TEXT_SHOW_UNIT: None,
    const.CUSTOM_TEXT_LINE_BREAK: None,
}

DEFAULT_CONNECTION = {
    const.SETTING_HOST: const.EMPTY_STRING,
    const.SETTING_PORT: const.EMPTY_STRING,
    const.SETTING_SSL: True,
    const.SETTING_VERIFY_CERTIFICATE: True,
    const.SETTING_TOKEN: const.EMPTY_STRING
}

DEFAULT_ACTION = {
    const.SETTING_VERSION: 1,
    const.SETTING_UUID: const.EMPTY_STRING,

    const.SETTING_ENTITY: {
        const.SETTING_DOMAIN: const.EMPTY_STRING,
        const.SETTING_ENTITY: const.EMPTY_STRING
    },

    const.SETTING_SERVICE: {
        const.SETTING_CALL_SERVICE: const.DEFAULT_SERVICE_CALL_SERVICE,
        const.SETTING_SERVICE: const.EMPTY_STRING,
        const.SETTING_PARAMETERS: {}
    },

    const.SETTING_ICON: {
        const.SETTING_SHOW_ICON: const.DEFAULT_ICON_SHOW_ICON,
        const.SETTING_ICON: const.EMPTY_STRING,
        const.SETTING_COLOR: const.DEFAULT_ICON_COLOR,
        const.SETTING_SCALE: const.DEFAULT_ICON_SCALE,
        const.SETTING_OPACITY: const.DEFAULT_ICON_OPACITY,
        const.SETTING_CUSTOMIZATIONS: []
    },

    const.SETTING_TEXT: {
        const.SETTING_SHOW_TEXT: const.DEFAULT_TEXT_SHOW_TEXT,
        const.SETTING_POSITION: const.DEFAULT_TEXT_POSITION,
        const.SETTING_ATTRIBUTE: const.STATE,
        const.SETTING_ROUND: const.DEFAULT_TEXT_ROUND,
        const.SETTING_ROUND_PRECISION: const.DEFAULT_TEXT_ROUND_PRECISION,
        const.SETTING_TEXT_SIZE: const.DEFAULT_TEXT_TEXT_SIZE,
        const.SETTING_TEXT_COLOR: const.DEFAULT_TEXT_TEXT_COLOR,
        const.SETTING_OUTLINE_SIZE: const.DEFAULT_TEXT_OUTLINE_SIZE,
        const.SETTING_OUTLINE_COLOR: const.DEFAULT_TEXT_OUTLINE_COLOR,
        const.SETTING_SHOW_UNIT: const.DEFAULT_TEXT_SHOW_UNIT,
        const.SETTING_UNIT_LINE_BREAK: const.DEFAULT_TEXT_UNIT_LINE_BREAK,
        const.SETTING_CUSTOMIZATIONS: []
    }
}


def get_action_settings(existing: Dict[str, Any]) -> Dict[str, Any]:
    """
    This method takes an action settings dict and fills all missing settings with default values.
    Settings present in the existing settings dict, which are not needed anymore, are removed.
    """
    settings = copy.deepcopy(DEFAULT_ACTION)

    for key, value in existing.items():
        if key in settings and key != const.SETTING_VERSION:
            # apply all settings except for the version
            settings[key] = value

    # remove unused keys in customizations
    for index, customization in enumerate(settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS]):
        settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS][index] = filter_dicts(customization, CUSTOM_ICON)

    for index, customization in enumerate(settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS]):
        settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS][index] = filter_dicts(customization, CUSTOM_TEXT)

    if settings[const.SETTING_UUID] == const.EMPTY_STRING:
        settings[const.SETTING_UUID] = str(uuid.uuid4())

    return settings


def get_connection_settings(existing: Dict[str, Any]) -> Dict[str, Any]:
    """
    This method takes a connection settings dict and fills all missing settings with default values.
    Settings present in the existing settings dict, which are not needed anymore, are removed.
    """
    settings = copy.deepcopy(DEFAULT_CONNECTION)

    for key, value in existing.items():
        if key in settings:
            settings[key] = value

    return settings


def migrate(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for all migration calls.
    """
    if not settings:
        # this is a new action
        return DEFAULT_ACTION.copy()

    result = settings.copy()

    result = migrate_call_service_moved_to_expander(result)
    result = migrate_setting_text_size_moved_to_text_text_size(result)
    result = migrate_setting_customization_icons_to_icon(result)

    if result.get(const.SETTING_VERSION, 0) < 1:
        result = migrate_v0_to_v1(result)

    return result


def migrate_v0_to_v1(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate from version 0 to version 1 of the settings.
    Change colors from range [0-1] to range [0-255] and add default alpha value
    Move settings to new structure
    Added 2025/04/01
    """

    # migrate customizations and colors
    if settings.get(const.SETTING_ICON_COLOR):
        settings[const.SETTING_ICON_COLOR] = [int(c * 255) for c in settings[const.SETTING_ICON_COLOR]]
        settings[const.SETTING_ICON_COLOR].append(255)
    if settings.get(const.SETTING_TEXT_TEXT_COLOR):
        settings[const.SETTING_TEXT_TEXT_COLOR] = [int(c * 255) for c in settings[const.SETTING_TEXT_TEXT_COLOR]]
        settings[const.SETTING_TEXT_TEXT_COLOR].append(255)
    if settings.get(const.SETTING_TEXT_OUTLINE_COLOR):
        settings[const.SETTING_TEXT_OUTLINE_COLOR] = [int(c * 255) for c in settings[const.SETTING_TEXT_OUTLINE_COLOR]]
        settings[const.SETTING_TEXT_OUTLINE_COLOR].append(255)

    for customization in settings.get(const.SETTING_CUSTOMIZATION_ICON, []):
        customization[const.CUSTOM_CONDITION] = {}
        customization[const.CUSTOM_CONDITION][const.CUSTOM_ATTRIBUTE] = customization[const.CUSTOM_ATTRIBUTE]
        customization[const.CUSTOM_CONDITION][const.CUSTOM_OPERATOR] = customization[const.CUSTOM_OPERATOR]
        customization[const.CUSTOM_CONDITION][const.CUSTOM_VALUE] = customization[const.CUSTOM_VALUE]

        if customization.get(const.CUSTOM_ICON_COLOR):
            customization[const.CUSTOM_ICON_COLOR] = [int(c * 255) for c in customization[const.CUSTOM_ICON_COLOR]]
            customization[const.CUSTOM_ICON_COLOR].append(255)

    for customization in settings.get(const.SETTING_CUSTOMIZATION_TEXT, []):
        customization[const.CUSTOM_CONDITION] = {}
        customization[const.CUSTOM_CONDITION][const.CUSTOM_ATTRIBUTE] = customization[const.CUSTOM_ATTRIBUTE]
        customization[const.CUSTOM_CONDITION][const.CUSTOM_OPERATOR] = customization[const.CUSTOM_OPERATOR]
        customization[const.CUSTOM_CONDITION][const.CUSTOM_VALUE] = customization[const.CUSTOM_VALUE]

        if customization.get(const.CUSTOM_TEXT_TEXT_COLOR):
            customization[const.CUSTOM_TEXT_TEXT_COLOR] = [int(c * 255) for c in
                                                           customization[const.CUSTOM_TEXT_TEXT_COLOR]]
            customization[const.CUSTOM_TEXT_TEXT_COLOR].append(255)
        if customization.get(const.CUSTOM_TEXT_OUTLINE_COLOR):
            customization[const.CUSTOM_TEXT_OUTLINE_COLOR] = [int(c * 255) for c in
                                                              customization[const.CUSTOM_TEXT_OUTLINE_COLOR]]
            customization[const.CUSTOM_TEXT_OUTLINE_COLOR].append(255)

    # migrate entity settings
    settings[const.SETTING_ENTITY] = {}
    settings[const.SETTING_ENTITY][const.SETTING_DOMAIN] = settings.get(const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING)
    settings[const.SETTING_ENTITY][const.SETTING_ENTITY] = settings.get(const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING)

    # migrate service settings
    settings[const.SETTING_SERVICE] = {}
    settings[const.SETTING_SERVICE][const.SETTING_CALL_SERVICE] = settings.get(const.SETTING_SERVICE_CALL_SERVICE,
                                                                               const.DEFAULT_SERVICE_CALL_SERVICE)
    settings[const.SETTING_SERVICE][const.SETTING_SERVICE] = settings.get(const.SETTING_SERVICE_SERVICE,
                                                                          const.EMPTY_STRING)
    settings[const.SETTING_SERVICE][const.SETTING_PARAMETERS] = {}
    for key, value in settings.get("service.service_parameters", {}).items():
        settings[const.SETTING_SERVICE][const.SETTING_PARAMETERS][key] = value

    # migrate icon settings
    settings[const.SETTING_ICON] = {}
    settings[const.SETTING_ICON][const.SETTING_SHOW_ICON] = settings.get(const.SETTING_ICON_SHOW_ICON,
                                                                         const.DEFAULT_ICON_SHOW_ICON)
    settings[const.SETTING_ICON][const.SETTING_ICON] = settings.get(const.SETTING_ICON_ICON, const.EMPTY_STRING)
    settings[const.SETTING_ICON][const.SETTING_COLOR] = settings.get(const.SETTING_ICON_COLOR, const.DEFAULT_ICON_COLOR)
    settings[const.SETTING_ICON][const.SETTING_SCALE] = settings.get(const.SETTING_ICON_SCALE, const.DEFAULT_ICON_SCALE)
    settings[const.SETTING_ICON][const.SETTING_OPACITY] = settings.get(const.SETTING_ICON_OPACITY,
                                                                       const.DEFAULT_ICON_OPACITY)
    settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS] = settings.get(const.SETTING_CUSTOMIZATION_ICON, [])

    # migrate text settings
    settings[const.SETTING_TEXT] = {}
    settings[const.SETTING_TEXT][const.SETTING_SHOW_TEXT] = settings.get(const.SETTING_TEXT_SHOW_TEXT,
                                                                         const.DEFAULT_TEXT_SHOW_TEXT)
    settings[const.SETTING_TEXT][const.SETTING_POSITION] = settings.get(const.SETTING_TEXT_POSITION,
                                                                        const.DEFAULT_TEXT_POSITION)
    settings[const.SETTING_TEXT][const.SETTING_ATTRIBUTE] = settings.get(const.SETTING_TEXT_ATTRIBUTE,
                                                                         const.DEFAULT_TEXT_ATTRIBUTE)
    settings[const.SETTING_TEXT][const.SETTING_ROUND] = settings.get(const.SETTING_TEXT_ROUND, const.DEFAULT_TEXT_ROUND)
    settings[const.SETTING_TEXT][const.SETTING_ROUND_PRECISION] = settings.get(const.SETTING_TEXT_ROUND_PRECISION,
                                                                               const.DEFAULT_TEXT_ROUND_PRECISION)
    settings[const.SETTING_TEXT][const.SETTING_TEXT_SIZE] = settings.get(const.SETTING_TEXT_TEXT_SIZE,
                                                                         const.DEFAULT_TEXT_TEXT_SIZE)
    settings[const.SETTING_TEXT][const.SETTING_TEXT_COLOR] = settings.get(const.SETTING_TEXT_TEXT_COLOR,
                                                                          const.DEFAULT_TEXT_TEXT_COLOR)
    settings[const.SETTING_TEXT][const.SETTING_OUTLINE_SIZE] = settings.get(const.SETTING_TEXT_OUTLINE_SIZE,
                                                                            const.DEFAULT_TEXT_OUTLINE_SIZE)
    settings[const.SETTING_TEXT][const.SETTING_OUTLINE_COLOR] = settings.get(const.SETTING_TEXT_OUTLINE_COLOR,
                                                                             const.DEFAULT_TEXT_OUTLINE_COLOR)
    settings[const.SETTING_TEXT][const.SETTING_SHOW_UNIT] = settings.get(const.SETTING_TEXT_SHOW_UNIT,
                                                                         const.DEFAULT_TEXT_SHOW_UNIT)
    settings[const.SETTING_TEXT][const.SETTING_UNIT_LINE_BREAK] = settings.get(const.SETTING_TEXT_UNIT_LINE_BREAK,
                                                                               const.DEFAULT_TEXT_UNIT_LINE_BREAK)
    settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS] = settings.get(const.SETTING_CUSTOMIZATION_TEXT, [])

    return settings


def migrate_setting_customization_icons_to_icon(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks if the key "customization.icons" is present and moves it to the new "customization.icon".
    Added 2025/03/11
    """
    if settings.get("customization.icons"):
        settings[const.SETTING_CUSTOMIZATION_ICON] = settings["customization.icons"]

    return settings


def migrate_setting_text_size_moved_to_text_text_size(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks if the text size is set under the old key and moves it to the new one.
    Added 2025/03/11
    """
    if settings.get("text.size"):
        settings[const.SETTING_TEXT_TEXT_SIZE] = settings["text.size"]

    return settings


def migrate_call_service_moved_to_expander(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks if call_service is present in the settings. If not, it checks for a service being
    defined to be called. If there is one, call_service is set to true, else it is false.
    Added 2024/07/10
    """
    if settings.get(const.SETTING_SERVICE_CALL_SERVICE) is None and settings.get(
            const.SETTING_SERVICE_SERVICE):
        settings[const.SETTING_SERVICE_CALL_SERVICE] = True

    return settings


def filter_dicts(dict1, dict2):
    """
    Remove keys from dict1 that are not present in dict2.
    If the value of a key is a dict, apply the same filtering recursively.

    Args:
    dict1 (dict): The dictionary to be filtered.
    dict2 (dict): The dictionary to check against.

    Returns:
    dict: The filtered dictionary.
    """
    filtered_dict = {}
    for key in dict1:
        if key in dict2:
            # If the value is a dictionary, recurse into it
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                filtered_dict[key] = filter_dicts(dict1[key], dict2[key])
            else:
                filtered_dict[key] = dict1[key]
    return filtered_dict
