"""
The module for settings control.
"""
import copy
from typing import Dict, Any

from de_gensyn_HomeAssistantPlugin import const

VALID_KEYS_CUSTOM_BASE = [
    const.CUSTOM_ATTRIBUTE,
    const.CUSTOM_OPERATOR,
    const.CUSTOM_VALUE
]

VALID_KEYS_CUSTOM_ICON = [
    const.CUSTOM_ICON_ICON,
    const.CUSTOM_ICON_COLOR,
    const.CUSTOM_ICON_SCALE,
    const.CUSTOM_ICON_OPACITY
]

VALID_KEYS_CUSTOM_TEXT = [
    const.CUSTOM_TEXT_POSITION,
    const.CUSTOM_TEXT_ATTRIBUTE,
    const.CUSTOM_TEXT_CUSTOM_TEXT,
    const.CUSTOM_TEXT_ROUND,
    const.CUSTOM_TEXT_ROUND_PRECISION,
    const.CUSTOM_TEXT_TEXT_SIZE,
    const.CUSTOM_TEXT_TEXT_COLOR,
    const.CUSTOM_TEXT_OUTLINE_SIZE,
    const.CUSTOM_TEXT_OUTLINE_COLOR,
    const.CUSTOM_TEXT_SHOW_UNIT,
    const.CUSTOM_TEXT_LINE_BREAK,
]

DEFAULT_CONNECTION = {
    const.SETTING_HOST: const.EMPTY_STRING,
    const.SETTING_PORT: const.EMPTY_STRING,
    const.SETTING_SSL: True,
    const.SETTING_VERIFY_CERTIFICATE: True,
    const.SETTING_TOKEN: const.EMPTY_STRING
}

DEFAULT_ACTION = {
    const.SETTING_ENTITY_DOMAIN: const.EMPTY_STRING,
    const.SETTING_ENTITY_ENTITY: const.EMPTY_STRING,

    const.SETTING_SERVICE_CALL_SERVICE: const.DEFAULT_SERVICE_CALL_SERVICE,
    const.SETTING_SERVICE_SERVICE: const.EMPTY_STRING,
    const.SETTING_SERVICE_PARAMETERS: {},

    const.SETTING_ICON_SHOW_ICON: const.DEFAULT_ICON_SHOW_ICON,
    const.SETTING_ICON_ICON: const.EMPTY_STRING,
    const.SETTING_ICON_COLOR: const.DEFAULT_ICON_COLOR,
    const.SETTING_ICON_SCALE: const.DEFAULT_ICON_SCALE,
    const.SETTING_ICON_OPACITY: const.DEFAULT_ICON_OPACITY,

    const.SETTING_TEXT_SHOW_TEXT: const.DEFAULT_TEXT_SHOW_TEXT,
    const.SETTING_TEXT_POSITION: const.DEFAULT_TEXT_POSITION,
    const.SETTING_TEXT_ATTRIBUTE: const.STATE,
    const.SETTING_TEXT_ROUND: const.DEFAULT_TEXT_ROUND,
    const.SETTING_TEXT_ROUND_PRECISION: const.DEFAULT_TEXT_ROUND_PRECISION,
    const.SETTING_TEXT_TEXT_SIZE: const.DEFAULT_TEXT_TEXT_SIZE,
    const.SETTING_TEXT_TEXT_COLOR: const.DEFAULT_TEXT_TEXT_COLOR,
    const.SETTING_TEXT_OUTLINE_SIZE: const.DEFAULT_TEXT_OUTLINE_SIZE,
    const.SETTING_TEXT_OUTLINE_COLOR: const.DEFAULT_TEXT_OUTLINE_COLOR,
    const.SETTING_TEXT_SHOW_UNIT: const.DEFAULT_TEXT_SHOW_UNIT,
    const.SETTING_TEXT_UNIT_LINE_BREAK: const.DEFAULT_TEXT_UNIT_LINE_BREAK,

    const.SETTING_DIAL_ENTITY_DOMAIN: const.EMPTY_STRING,
    const.SETTING_DIAL_ENTITY_ENTITY: const.EMPTY_STRING,

    const.SETTING_DIAL_SERVICE_CALL_SERVICE: const.DEFAULT_SERVICE_CALL_SERVICE,
    const.SETTING_DIAL_SERVICE_SERVICE: const.EMPTY_STRING,
    const.SETTING_DIAL_STEP_SIZE: const.DEFAULT_DIAL_STEP_SIZE,

    const.SETTING_CUSTOMIZATION_ICON: [],
    const.SETTING_CUSTOMIZATION_TEXT: []
}


def get_action_settings(existing: Dict[str, Any]) -> Dict[str, Any]:
    """
    This method takes an action settings dict and fills all missing settings with default values.
    Settings present in the existing settings dict, which are not needed anymore, are removed.
    """
    settings = copy.deepcopy(DEFAULT_ACTION)

    for key, value in existing.items():
        if key in settings:
            settings[key] = value

    # remove unused keys in customizations
    for custom_icon in settings[const.SETTING_CUSTOMIZATION_ICON]:
        for key in custom_icon:
            if key not in VALID_KEYS_CUSTOM_BASE and key not in VALID_KEYS_CUSTOM_ICON:
                custom_icon.pop(key)

    for custom_text in settings[const.SETTING_CUSTOMIZATION_TEXT]:
        for key in custom_text:
            if key not in VALID_KEYS_CUSTOM_BASE and key not in VALID_KEYS_CUSTOM_TEXT:
                custom_text.pop(key)

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
    result = settings.copy()

    result = migrate_call_service_moved_to_expander(result)
    result = migrate_setting_text_size_moved_to_text_text_size(result)
    result = migrate_setting_customization_icons_to_icon(result)

    return result


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
