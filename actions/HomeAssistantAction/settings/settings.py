"""
Module to manage HomeAssistantPlugin action settings.
"""

import copy
from typing import Dict, Any, Tuple, List

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction import const
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.icon_customization import IconCustomization
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.customization.text_customization import TextCustomization
from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.settings import settings_helper


class Settings:
    """
    Class to manage all settings for an HomeAssistantPlugin action.
    :param action: the action whose settings are being managed
    """
    def __init__(self, action):
        self.action = action

        settings = settings_helper.migrate(self.action.get_settings())
        settings = settings_helper.get_action_settings(settings)

        self.settings = settings
        self.action.set_settings(self.settings)

    def set_settings(self, settings: Dict[str, Any]) -> None:
        """
        Applies and saves the settings.
        :param settings: the new settings
        """
        self.settings = settings
        self.action.set_settings(self.settings)

    def get_uuid(self) -> str:
        """
        Get the uuid.
        :return: the uuid
        """
        return self.settings[const.SETTING_UUID]

    def get_domain(self) -> str:
        """
        Get the domain.
        :return: the domain
        """
        return self.settings[const.SETTING_ENTITY][const.SETTING_DOMAIN]

    def get_entity(self) -> str:
        """
        Get the entity.
        :return: the entity
        """
        return self.settings[const.SETTING_ENTITY][const.SETTING_ENTITY]

    def get_call_service(self) -> str:
        """
        Get whether to call a service.
        :return: whether to call a service
        """
        return self.settings[const.SETTING_SERVICE][const.SETTING_CALL_SERVICE]

    def get_service(self) -> str:
        """
        Get the service.
        :return: the service
        """
        return self.settings[const.SETTING_SERVICE][const.SETTING_SERVICE]

    def get_service_parameters(self) -> Dict:
        """
        Retrieve all service parameters.
        :return: all service parameters
        """
        return self.settings[const.SETTING_SERVICE][const.ACTION_PARAMETERS]

    def set_service_parameter(self, field, value) -> None:
        """
        Set the service parameter for the field.
        :param field: the field to set
        :param value: the value for the field
        """
        self.settings[const.SETTING_SERVICE][const.ACTION_PARAMETERS][field] = value
        self.action.set_settings(self.settings)

    def remove_service_parameter(self, field) -> None:
        """
        Remove the service parameter for the field.
        :param field: the field to remove
        """
        self.settings[const.SETTING_SERVICE][const.ACTION_PARAMETERS].pop(field)
        self.action.set_settings(self.settings)

    def clear_service_parameters(self) -> None:
        """
        Clear all service parameters.
        """
        self.settings[const.SETTING_SERVICE][const.ACTION_PARAMETERS] = {}
        self.action.set_settings(self.settings)

    def get_show_icon(self) -> bool:
        """
        Get whether to show the icon.
        :return: whether to show the icon
        """
        return self.settings[const.SETTING_ICON][const.SETTING_SHOW_ICON]

    def get_icon(self) -> str:
        """
        Get the icon.
        :return:the icon
        """
        return self.settings[const.SETTING_ICON][const.SETTING_ICON]

    def get_icon_color(self) -> Tuple[int, int, int, int]:
        """
        Get the icon color.
        :return:the icon color
        """
        return self.settings[const.SETTING_ICON][const.SETTING_COLOR]

    def get_icon_scale(self) -> int:
        """
        Get the icon scale.
        :return: the icon scale
        """
        return int(self.settings[const.SETTING_ICON][const.SETTING_SCALE])

    def get_icon_opacity(self) -> int:
        """
        Get the icon opacity.
        :return: the icon opacity
        """
        return int(self.settings[const.SETTING_ICON][const.SETTING_OPACITY])

    def get_icon_customizations(self) -> List[IconCustomization]:
        """
        Retrieve all icon customizations.
        :return: all icon customizations
        """
        customizations = self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS]

        result = []

        for c in customizations:
            attribute = c[const.CUSTOM_CONDITION][const.CUSTOM_ATTRIBUTE]
            operator = c[const.CUSTOM_CONDITION][const.CUSTOM_OPERATOR]
            value = c[const.CUSTOM_CONDITION][const.CUSTOM_VALUE]
            icon = c[const.CUSTOM_ICON_ICON] if const.CUSTOM_ICON_ICON in c else None
            color = c[const.CUSTOM_ICON_COLOR] if const.CUSTOM_ICON_COLOR in c else None
            scale = c[const.CUSTOM_ICON_SCALE] if const.CUSTOM_ICON_SCALE in c else None
            opacity = c[const.CUSTOM_ICON_OPACITY] if const.CUSTOM_ICON_OPACITY in c else None

            result.append(IconCustomization(attribute, operator, value, icon, color, scale, opacity))

        return result

    def move_icon_customization(self, index: int, places_count: int):
        """
        Move the icon customization at the index by x places.
        :param index: the index to move
        :param places_count: to number of places to move; may be negative
        :return:
        """
        customization_list = self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS]
        self._move_customization(customization_list, index, places_count)

    def remove_icon_customization(self, index: int) -> None:
        """
        Remove the icon customization at the index.
        :param index: the index to remove
        :return:
        """
        self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS].pop(index)
        self.action.set_settings(self.settings)

    def replace_icon_customization(self, index: int, customization: IconCustomization) -> None:
        """
        Replace the icon customization at the index.
        :param index: the index to replace
        :param customization: the new customization
        :return:
        """
        self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS][index] = customization.export()
        self.action.set_settings(self.settings)

    def add_icon_customization(self, customization: IconCustomization) -> None:
        """
        Add a new icon customization.
        :param customization: the new customization
        """
        self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS].append(customization.export())
        self.action.set_settings(self.settings)

    def get_show_text(self) -> bool:
        """
        Get whether to show text.
        :return: whether to show text
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_SHOW_TEXT]

    def get_text_position(self) -> str:
        """
        Get the text position.
        :return: the text position
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_POSITION]

    def get_text_attribute(self) -> str:
        """
        Get the text attribute.
        :return: the text attribute
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_ATTRIBUTE]

    def get_text_round(self) -> bool:
        """
        Get whether to round the text value.
        :return: whether to round the text value
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_ROUND]

    def get_text_round_precision(self) -> int:
        """
        Get the text round precision.
        :return: the text round precision
        """
        return int(self.settings[const.SETTING_TEXT][const.SETTING_ROUND_PRECISION])

    def get_text_text_size(self) -> int:
        """
        Get the text size.
        :return: the text size
        """
        return int(self.settings[const.SETTING_TEXT][const.SETTING_TEXT_SIZE])

    def get_text_text_color(self) -> Tuple[int, int, int, int]:
        """
        Get the text color.
        :return: the text color
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_TEXT_COLOR]

    def get_text_outline_size(self) -> int:
        """
        Get the text outline size.
        :return: the text outline size
        """
        return int(self.settings[const.SETTING_TEXT][const.SETTING_OUTLINE_SIZE])

    def get_text_outline_color(self) -> Tuple[int, int, int, int]:
        """
        Get the text outline color.
        :return: the text outline color
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_OUTLINE_COLOR]

    def get_text_show_unit(self) -> bool:
        """
        Get whether to show the unit of measurement.
        :return: whether to show the unit of measurement
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_SHOW_UNIT]

    def get_text_unit_line_break(self) -> bool:
        """
        Get whether to show a line break between value and unit.
        :return: whether to show a line break between value and unit
        """
        return self.settings[const.SETTING_TEXT][const.SETTING_UNIT_LINE_BREAK]

    def get_text_customizations(self) -> List[TextCustomization]:
        """
        Retrieve all text customizations.
        :return: all text customizations
        """
        customizations = self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS]

        result = []

        for c in customizations:
            attribute = c[const.CUSTOM_CONDITION][const.CUSTOM_ATTRIBUTE]
            operator = c[const.CUSTOM_CONDITION][const.CUSTOM_OPERATOR]
            value = c[const.CUSTOM_CONDITION][const.CUSTOM_VALUE]
            position = c[const.CUSTOM_TEXT_POSITION] if const.CUSTOM_TEXT_POSITION in c else None
            text_attribute = c[const.CUSTOM_TEXT_ATTRIBUTE] if const.CUSTOM_TEXT_ATTRIBUTE in c else None
            custom_text = c[const.CUSTOM_TEXT_CUSTOM_TEXT] if const.CUSTOM_TEXT_CUSTOM_TEXT in c else None
            do_round = c[const.CUSTOM_TEXT_ROUND] if const.CUSTOM_TEXT_ROUND in c else None
            round_precision = c[const.CUSTOM_TEXT_ROUND_PRECISION] if const.CUSTOM_TEXT_ROUND_PRECISION in c else None
            text_size = c[const.CUSTOM_TEXT_TEXT_SIZE] if const.CUSTOM_TEXT_TEXT_SIZE in c else None
            text_color = c[const.CUSTOM_TEXT_TEXT_COLOR] if const.CUSTOM_TEXT_TEXT_COLOR in c else None
            outline_size = c[const.CUSTOM_TEXT_OUTLINE_SIZE] if const.CUSTOM_TEXT_OUTLINE_SIZE in c else None
            outline_color = c[const.CUSTOM_TEXT_OUTLINE_COLOR] if const.CUSTOM_TEXT_OUTLINE_COLOR in c else None
            show_unit = c[const.CUSTOM_TEXT_SHOW_UNIT] if const.CUSTOM_TEXT_SHOW_UNIT in c else None
            line_break = c[const.CUSTOM_TEXT_LINE_BREAK] if const.CUSTOM_TEXT_LINE_BREAK in c else None

            result.append(TextCustomization(attribute, operator, value, position, text_attribute, custom_text, do_round,
                                            round_precision, text_size, text_color, outline_size, outline_color,
                                            show_unit, line_break))

        return result

    def move_text_customization(self, index: int, places_count: int):
        """
        Move the text customization at the index by x places.
        :param index: the index to move
        :param places_count: to number of places to move; may be negative
        :return:
        """
        customization_list = self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS]
        self._move_customization(customization_list, index, places_count)

    def remove_text_customization(self, index: int) -> None:
        """
        Remove the text customization at the index.
        :param index: the index to remove
        :return:
        """
        self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS].pop(index)
        self.action.set_settings(self.settings)

    def replace_text_customization(self, index: int, customization: TextCustomization) -> None:
        """
        Replace the text customization at the index.
        :param index: the index to replace
        :param customization: the new customization
        :return:
        """
        self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS][index] = customization.export()
        self.action.set_settings(self.settings)

    def add_text_customization(self, customization: TextCustomization) -> None:
        """
        Add a new text customization.
        :param customization: the new customization
        """
        self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS].append(customization.export())
        self.action.set_settings(self.settings)

    def reset(self, domain: str) -> None:
        """
        Empty the settings and keep only the UUID and the given domain.
        :param domain: the new domain
        """
        action_id = self.settings[const.SETTING_UUID]
        self.settings = copy.deepcopy(settings_helper.DEFAULT_ACTION)
        self.settings[const.SETTING_UUID] = action_id
        self.settings[const.SETTING_ENTITY][const.SETTING_DOMAIN] = domain
        self.action.set_settings(self.settings)

    def _move_customization(self, customization_list: List, index: int, places_count: int):
        customization = customization_list.pop(index)
        customization_list.insert(index + places_count, customization)
        self.action.set_settings(self.settings)
