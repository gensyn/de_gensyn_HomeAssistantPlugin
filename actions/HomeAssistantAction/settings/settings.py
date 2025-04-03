from typing import Dict, Any, Tuple, List

from de_gensyn_HomeAssistantPlugin import const

class Settings:
    def __init__(self, action, settings: Dict[str, Any]):
        self.action = action
        self.settings = settings
        self.action.set_settings(self.settings)

    def set_settings(self, settings: Dict[str, Any]):
        self.settings = settings
        self.action.set_settings(self.settings)
    
    def get_uuid(self) -> str:
        return self.settings[const.SETTING_UUID]

    def get_domain(self) -> str:
        return self.settings[const.SETTING_ENTITY][const.SETTING_DOMAIN]
    
    def get_entity(self) -> str:
        return self.settings[const.SETTING_ENTITY][const.SETTING_ENTITY]
    
    def get_service(self) -> str:
        return self.settings[const.SETTING_SERVICE][const.SETTING_SERVICE]
    
    def get_service_parameters(self) -> Dict:
        return self.settings[const.SETTING_SERVICE][const.SETTING_PARAMETERS]

    def set_service_parameter(self, field, value) -> None:
        self.settings[const.SETTING_SERVICE][const.SETTING_PARAMETERS][field] = value
        self.action.set_settings(self.settings)

    def remove_service_parameter(self, field) -> None:
        self.settings[const.SETTING_SERVICE][const.SETTING_PARAMETERS].pop(field)
        self.action.set_settings(self.settings)

    def clear_service_parameters(self) -> None:
        self.settings[const.SETTING_SERVICE][const.SETTING_PARAMETERS] = {}
        self.action.set_settings(self.settings)
    
    def get_show_icon(self) -> bool:
        return self.settings[const.SETTING_ICON][const.SETTING_SHOW_ICON]
    
    def get_icon(self) -> str:
        return self.settings[const.SETTING_ICON][const.SETTING_ICON]
    
    def get_icon_color(self) -> Tuple[int, int, int, int]:
        return self.settings[const.SETTING_ICON][const.SETTING_COLOR]
    
    def get_icon_scale(self) -> int:
        return self.settings[const.SETTING_ICON][const.SETTING_SCALE]
    
    def get_icon_opacity(self) -> int:
        return self.settings[const.SETTING_ICON][const.SETTING_OPACITY]
    
    def get_icon_customizations(self) -> List:
        return self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS]

    def set_icon_customizations(self, customizations: List) -> None:
        self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS] = customizations
        self.action.set_settings(self.settings)

    def remove_icon_customization(self, index: int) -> None:
        self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS].pop(index)
        self.action.set_settings(self.settings)

    def replace_icon_customization(self, index: int, customization: Dict) -> None:
        self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS][index] = customization
        self.action.set_settings(self.settings)

    def add_icon_customization(self, customization: Dict) -> None:
        self.settings[const.SETTING_ICON][const.SETTING_CUSTOMIZATIONS].append(customization)
        self.action.set_settings(self.settings)

    def get_show_text(self) -> bool:
        return self.settings[const.SETTING_TEXT][const.SETTING_SHOW_TEXT]

    def get_text_position(self) -> str:
        return self.settings[const.SETTING_TEXT][const.SETTING_POSITION]

    def get_text_attribute(self) -> str:
        return self.settings[const.SETTING_TEXT][const.SETTING_ATTRIBUTE]

    def get_text_round(self) -> bool:
        return self.settings[const.SETTING_TEXT][const.SETTING_ROUND]

    def get_text_round_precision(self) -> int:
        return self.settings[const.SETTING_TEXT][const.SETTING_ROUND_PRECISION]

    def get_text_text_size(self) -> int:
        return self.settings[const.SETTING_TEXT][const.SETTING_TEXT_SIZE]

    def get_text_text_color(self) -> Tuple[int, int, int, int]:
        return self.settings[const.SETTING_TEXT][const.SETTING_TEXT_COLOR]

    def get_text_outline_size(self) -> int:
        return self.settings[const.SETTING_TEXT][const.SETTING_OUTLINE_SIZE]

    def get_text_outline_color(self) -> Tuple[int, int, int, int]:
        return self.settings[const.SETTING_TEXT][const.SETTING_OUTLINE_COLOR]

    def get_text_show_unit(self) -> bool:
        return self.settings[const.SETTING_TEXT][const.SETTING_SHOW_UNIT]

    def get_text_unit_line_break(self) -> bool:
        return self.settings[const.SETTING_TEXT][const.SETTING_UNIT_LINE_BREAK]

    def get_text_customizations(self) -> List:
        return self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS]

    def set_text_customizations(self, customizations: List) -> None:
        self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS] = customizations
        self.action.set_settings(self.settings)

    def remove_text_customization(self, index: int) -> None:
        self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS].pop(index)
        self.action.set_settings(self.settings)

    def replace_text_customization(self, index: int, customization: Dict) -> None:
        self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS][index] = customization
        self.action.set_settings(self.settings)

    def add_text_customization(self, customization: Dict) -> None:
        self.settings[const.SETTING_TEXT][const.SETTING_CUSTOMIZATIONS].append(customization)
        self.action.set_settings(self.settings)
