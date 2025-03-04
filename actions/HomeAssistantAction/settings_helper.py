"""
The module for settings control.
"""
from typing import Dict, Any

from de_gensyn_HomeAssistantPlugin import const

DEFAULT = {
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
    const.SETTING_TEXT_ATTRIBUTE: const.STATE,
    const.SETTING_TEXT_ROUND: const.DEFAULT_TEXT_ROUND,
    const.SETTING_TEXT_ROUND_PRECISION: const.DEFAULT_TEXT_ROUND_PRECISION,
    const.SETTING_TEXT_POSITION: const.DEFAULT_TEXT_POSITION,
    const.SETTING_TEXT_ADAPTIVE_SIZE: const.DEFAULT_TEXT_ADAPTIVE_SIZE,
    const.SETTING_TEXT_SIZE: const.DEFAULT_TEXT_SIZE,
    const.SETTING_TEXT_SHOW_UNIT: const.DEFAULT_TEXT_SHOW_UNIT,
    const.SETTING_TEXT_UNIT_LINE_BREAK: const.DEFAULT_TEXT_UNIT_LINE_BREAK,

    const.SETTING_CUSTOMIZATION_ICONS: []
}


def fill_defaults(existing: Dict[str, Any]) -> Dict[str, Any]:
    """
    This method takes a settings dict and fills all missing settings with default values.
    Settings present in the existing settings dict, which are not needed anymore, are removed.
    """
    settings = DEFAULT.copy()

    for key, value in existing.items():
        if key in settings.keys():
            settings[key] = value

    return settings


def migrate(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for all migration calls.
    """
    result = settings

    result = migrate_call_service_moved_to_expander(result)

    return result


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
