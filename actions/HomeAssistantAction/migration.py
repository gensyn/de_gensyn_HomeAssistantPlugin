"""
The module for migrating settings to the newest version.
"""

from typing import Dict, Any

from plugins.de_gensyn_HomeAssistantPlugin.const import (SETTING_TEXT_ATTRIBUTE,
                                                         STATE)


def migrate(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for all migration calls.
    """
    result = migrate_show_text_moved_to_expander(settings)

    return result


def migrate_show_text_moved_to_expander(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sets an empty attribute to "state", since this used to be implied in an empty attribute. Now
    it is explicit.
    """
    if not settings.get(SETTING_TEXT_ATTRIBUTE):
        settings[SETTING_TEXT_ATTRIBUTE] = STATE

    return settings
