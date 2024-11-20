"""
Module for text related operations.
"""

from typing import Dict

from de_gensyn_HomeAssistantPlugin import const


def get_text(state: Dict, settings: Dict):
    """
    Determine text, position and font size to show on StreamDeck.
    """
    text = str(state.get(const.STATE))
    text_length = len(text)
    text_height = 1
    attribute = settings.get(const.SETTING_TEXT_ATTRIBUTE)

    if attribute == const.STATE:
        if settings.get(const.SETTING_TEXT_SHOW_UNIT):
            unit = state.get(const.ATTRIBUTES, {}).get(const.ATTRIBUTE_UNIT_OF_MEASUREMENT,
                                                       const.EMPTY_STRING)

            if settings.get(const.SETTING_TEXT_UNIT_LINE_BREAK):
                text_length = max(len(text), len(unit))
                text = f"{text}\n{unit}"
                text_height = 2
            else:
                text = f"{text} {unit}"
                text_length = len(text)
    else:
        text = str(state.get(const.ATTRIBUTES, {}).get(attribute, const.EMPTY_STRING))
        text_length = len(text)

    if settings.get(const.SETTING_TEXT_ROUND, const.DEFAULT_TEXT_ROUND) and _is_float(text):
        precision = int \
            (settings.get(const.SETTING_TEXT_ROUND_PRECISION, const.DEFAULT_TEXT_ROUND_PRECISION))

        as_number = round(float(text), precision)

        if precision == 0:
            as_number = int(as_number)

        text = str(as_number)

    position = settings.get(const.SETTING_TEXT_POSITION)
    font_size = settings.get(const.SETTING_TEXT_SIZE)

    if settings.get(const.SETTING_TEXT_ADAPTIVE_SIZE):
        if text_length == 1:
            font_size = 50
        elif text_length == 2:
            font_size = 40
        else:
            font_size = 30 - 3 * (text_length - 3)

        if text_height > 1:
            # account for text with line break
            font_size = min(font_size, 35)

        # set minimal font size, smaller is not readable
        font_size = max(font_size, 10)

    return text, position, font_size


def _is_float(value: str):
    if not "." in value:
        return False

    try:
        float(value)
        return True
    except ValueError:
        return False
