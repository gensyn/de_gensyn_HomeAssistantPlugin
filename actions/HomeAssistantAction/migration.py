"""
The module for migrating settings to the newest version.
"""

from typing import Dict, Any

from plugins.de_gensyn_HomeAssistantPlugin.const import (SETTING_TEXT_ATTRIBUTE, STATE,
                                                         SETTING_SERVICE_CALL_SERVICE,
                                                         SETTING_SERVICE_SERVICE)


def migrate(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for all migration calls.
    """
    result = settings

    result = migrate_show_text_moved_to_expander(result)
    result = migrate_call_service_moved_to_expander(result)

    return result


def migrate_show_text_moved_to_expander(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sets an empty attribute to "state", since this used to be implied, but now it is explicit.
    Added 2024/07/10
    """
    if not settings.get(SETTING_TEXT_ATTRIBUTE):
        settings[SETTING_TEXT_ATTRIBUTE] = STATE

    return settings


def migrate_call_service_moved_to_expander(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks if call_service is present in the settings. If not, it checks for a service being
    defined to be called. If there is one, call_service is set to true, else it is false. Added
    2024/07/10
    """
    if settings.get(SETTING_SERVICE_CALL_SERVICE) is None:
        if settings.get(SETTING_SERVICE_SERVICE):
            settings[SETTING_SERVICE_CALL_SERVICE] = True
        else:
            settings[SETTING_SERVICE_CALL_SERVICE] = False

    return settings
