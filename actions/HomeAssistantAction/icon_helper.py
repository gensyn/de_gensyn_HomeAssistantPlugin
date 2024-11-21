"""
Module for icon related operations.
"""

import json
import logging
import os
from typing import Dict

from de_gensyn_HomeAssistantPlugin import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.domains_with_custom_icons import \
    DOMAINS_WITH_SERVICE_ICONS

MDI_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", const.MDI_SVG_JSON)

with open(MDI_FILENAME, "r", encoding="utf-8") as f:
    MDI_ICONS: Dict[str, str] = json.loads(f.read())


def get_icon(state: Dict, settings: Dict) -> str:
    """
    Get the item corresponding to the given state.
    """
    domain = settings.get(const.SETTING_ENTITY_DOMAIN)

    icon_name = _get_icon_name(state, settings)

    color = const.ICON_COLOR_ON if state.get(const.STATE) in (
        const.STATE_ON, const.STATE_HOME) else const.ICON_COLOR_OFF

    if domain in DOMAINS_WITH_SERVICE_ICONS.keys():
        service = settings.get(const.SETTING_SERVICE_SERVICE)

        if service in DOMAINS_WITH_SERVICE_ICONS[domain].keys():
            color = const.ICON_COLOR_ON

            if state.get(const.STATE) in DOMAINS_WITH_SERVICE_ICONS[domain][service].keys():
                icon_name = DOMAINS_WITH_SERVICE_ICONS[domain][service][state.get(const.STATE)]
            else:
                icon_name = DOMAINS_WITH_SERVICE_ICONS[domain][service]["default"]

    icon_path = _get_icon_path(icon_name)

    opacity = str(
        round(settings.get(const.SETTING_ICON_OPACITY, const.DEFAULT_ICON_OPACITY) / 100,
              2))

    icon = _get_icon_svg(icon_name, icon_path)

    return (
        icon
        .replace("<color>", color)
        .replace("<opacity>", opacity)
    )


def _get_icon_name(state: Dict, settings: Dict) -> str:  # pylint: disable=too-many-return-statements
    custom_icons = settings.get(const.SETTING_CUSTOMIZATION_ICONS, [])

    for custom_icon in custom_icons:
        if custom_icon["attribute"] == const.STATE:
            value = state[const.STATE]
        else:
            value = state[const.ATTRIBUTES].get(custom_icon["attribute"])

        custom_icon_value = custom_icon["value"]

        try:
            # if both values are numbers, convert them both to float
            # if one is int and one float, testing for equality might fail (21 vs 21.0 eg)
            value = float(value)
            custom_icon_value = float(custom_icon_value)
        except ValueError:
            pass

        operator = custom_icon["operator"]
        custom_icon = custom_icon["icon"]

        if operator == "==" and str(value) == str(custom_icon_value):
            return custom_icon

        if operator == "!=" and str(value) != str(custom_icon_value):
            return custom_icon

        if not isinstance(value, float):
            # other operators are only applicable to numbers
            continue

        try:
            custom_icon_value = float(custom_icon_value)
        except ValueError:
            logging.error("Could not convert custom value to float: %s",
                          custom_icon_value)
            continue

        if operator == "<" and value < custom_icon_value:
            return custom_icon

        if operator == "<=" and value <= custom_icon_value:
            return custom_icon

        if operator == ">" and value > custom_icon_value:
            return custom_icon

        if operator == ">=" and value >= custom_icon_value:
            return custom_icon

    return state.get(const.ATTRIBUTES, {}).get(const.ATTRIBUTE_ICON, const.EMPTY_STRING)


def _get_icon_path(name: str) -> str:
    """
    Get the SVG path for the icon's MDI name.
    """
    if "mdi:" in name:
        name = name.replace("mdi:", const.EMPTY_STRING)

    return MDI_ICONS.get(name, const.EMPTY_STRING)


def _get_icon_svg(name: str, path: str) -> str:
    """
    Build a complete SVG string from an icons' name and path.
    """
    if not path:
        return const.EMPTY_STRING

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 24 '
            f'24"><title>{name}</title><path d="{path}" fill="<color>" opacity="<opacity>" '
            f'/></svg>')
