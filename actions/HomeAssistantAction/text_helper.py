"""
Module for text related operations.
"""

from typing import Dict

from de_gensyn_HomeAssistantPlugin import const


def get_text(state: Dict, settings: Dict) -> (str, str, int, str, int, str):
    """
    Determine text, position and font size to show on StreamDeck.
    """
    position = settings.get(const.SETTING_TEXT_POSITION)
    text_size = settings.get(const.SETTING_TEXT_TEXT_SIZE)
    text_color = [int(c*255) for c in settings.get(const.SETTING_TEXT_TEXT_COLOR)]
    outline_size = settings.get(const.SETTING_TEXT_OUTLINE_SIZE)
    outline_color = [int(c*255) for c in settings.get(const.SETTING_TEXT_OUTLINE_COLOR)]

    if not state["connected"]:
        return "N/A", position, text_size, text_color, outline_size, outline_color

    text = str(state.get(const.STATE))
    attribute = settings.get(const.SETTING_TEXT_ATTRIBUTE)

    if attribute == const.STATE:
        text = _round_value(text, settings)

        if settings.get(const.SETTING_TEXT_SHOW_UNIT):
            unit = state.get(const.ATTRIBUTES, {}).get(const.ATTRIBUTE_UNIT_OF_MEASUREMENT,
                                                       const.EMPTY_STRING)

            if settings.get(const.SETTING_TEXT_UNIT_LINE_BREAK):
                text = f"{text}\n{unit}"
            else:
                text = f"{text} {unit}"
    else:
        text = str(state.get(const.ATTRIBUTES, {}).get(attribute, const.EMPTY_STRING))
        text = _round_value(text, settings)

    return text, position, text_size, text_color, outline_size, outline_color


def _round_value(text: str, settings: Dict) -> str:
    if not settings.get(const.SETTING_TEXT_ROUND, const.DEFAULT_TEXT_ROUND) or not _is_float(text):
        return text

    precision = int(
        settings.get(const.SETTING_TEXT_ROUND_PRECISION, const.DEFAULT_TEXT_ROUND_PRECISION))

    as_number = round(float(text), precision)

    if precision == 0:
        as_number = int(as_number)

    return str(as_number)


def _is_float(value: str) -> bool:
    if not "." in value:
        return False

    try:
        float(value)
        return True
    except ValueError:
        return False
