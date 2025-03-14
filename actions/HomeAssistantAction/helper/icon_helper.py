"""
Module for icon related operations.
"""

import json
import logging
import os
from typing import Dict

from de_gensyn_HomeAssistantPlugin import const

MDI_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..",
                            const.MDI_SVG_JSON)

with open(MDI_FILENAME, "r", encoding="utf-8") as f:
    MDI_ICONS: Dict[str, str] = json.loads(f.read())


def get_icon(state: Dict, settings: Dict) -> (str, float):
    """
    Get the item corresponding to the given state.
    """
    if not state["connected"]:
        return (_get_icon_svg(const.ICON_NETWORK_OFF).replace("<color>",
                                                              const.ICON_COLOR_RED).replace(
            "<opacity>", "1.0")), round(const.DEFAULT_ICON_SCALE / 100, 2)

    name, color, scale, opacity = _get_icon_settings(state, settings)

    # convert RGB color to hex
    color = (f'#{int(round(color[0] * 255, 0)):02X}{int(round(color[1] * 255, 0)):02X}'
             f'{int(round(color[2] * 255, 0)):02X}')

    icon = _get_icon_svg(name)

    return (icon.replace("<color>", color).replace("<opacity>", str(opacity))), scale


def _get_icon_settings(state: Dict, settings: Dict) -> (str, str, str, str):
    # default value for the icon is the icon set in HA
    name = state.get(const.ATTRIBUTES, {}).get(const.ATTRIBUTE_ICON, const.EMPTY_STRING)
    color = settings[const.SETTING_ICON_COLOR]
    scale = round(settings[const.SETTING_ICON_SCALE] / 100, 2)
    opacity = str(round(settings[const.SETTING_ICON_OPACITY] / 100, 2))

    if settings[const.SETTING_ICON_ICON] in MDI_ICONS.keys():
        name = settings[const.SETTING_ICON_ICON]

    #
    # Begin custom icon
    #

    customizations = settings[const.SETTING_CUSTOMIZATION_ICON]

    for customization in customizations:
        value = get_value(state, customization)

        custom_icon_value = customization[const.CUSTOM_VALUE]

        try:
            # if both values are numbers, convert them both to float
            # if one is int and one float, testing for equality might fail (21 vs 21.0 eg)
            value = float(value)
            custom_icon_value = float(custom_icon_value)
        except (ValueError, TypeError):
            pass

        operator = customization[const.CUSTOM_OPERATOR]

        if ((operator == "==" and str(value) == str(custom_icon_value))
                or (operator == "!=" and str(value) != str(custom_icon_value))):
            name, color, scale, opacity = _replace_values(name, color, scale, opacity,
                                                          customization)

        if not isinstance(value, float):
            # other operators are only applicable to numbers
            continue

        try:
            custom_icon_value = float(custom_icon_value)
        except ValueError:
            logging.error("Could not convert custom value to float: %s",
                          custom_icon_value)
            continue

        if ((operator == "<" and value < custom_icon_value)
                or (operator == "<=" and value <= custom_icon_value)
                or (operator == ">" and value > custom_icon_value)
                or (operator == ">=" and value >= custom_icon_value)):
            name, color, scale, opacity = _replace_values(name, color, scale, opacity,
                                                          customization)

    #
    # End custom icon
    #

    return name, color, scale, opacity


def get_value(state: Dict, customization: Dict):
    """
    Gets the current value that the customization references.
    """
    if customization[const.CUSTOM_ATTRIBUTE] == const.STATE:
        value = state[const.STATE]
    else:
        value = state[const.ATTRIBUTES].get(customization[const.CUSTOM_ATTRIBUTE])

    return value


def _replace_values(name: str, color: str, scale: float, opacity: str, customization: dict):
    ret_name = name
    ret_color = color
    ret_scale = scale
    ret_opacity = opacity

    if customization.get(const.CUSTOM_ICON_ICON) is not None:
        ret_name = customization[const.CUSTOM_ICON_ICON]

    if customization.get(const.CUSTOM_ICON_COLOR) is not None:
        ret_color = customization[const.CUSTOM_ICON_COLOR]

    if customization.get(const.CUSTOM_ICON_SCALE) is not None:
        ret_scale = round(customization[const.CUSTOM_ICON_SCALE] / 100, 2)

    if customization.get(const.CUSTOM_ICON_OPACITY) is not None:
        ret_opacity = round(customization[const.CUSTOM_ICON_OPACITY] / 100, 2)

    return ret_name, ret_color, ret_scale, ret_opacity


def _get_icon_path(name: str) -> str:
    """
    Get the SVG path for the icon's MDI name.
    """
    if "mdi:" in name:
        name = name.replace("mdi:", const.EMPTY_STRING)

    return MDI_ICONS.get(name, const.EMPTY_STRING)


def _get_icon_svg(name: str) -> str:
    """
    Build a complete SVG string from an icons' name and path.
    """
    path = _get_icon_path(name)

    if not path:
        return const.EMPTY_STRING

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 24 '
            f'24"><title>{name}</title><path d="{path}" fill="<color>" opacity="<opacity>" '
            f'/></svg>')
