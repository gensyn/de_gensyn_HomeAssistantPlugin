"""
Constants for the Home Assistant hass.
"""

EMPTY_STRING = ""
HOME_ASSISTANT_ACTION = "Home Assistant (Deprecated)"
ERROR = "error"

# HOME_ASSISTANT_ACTION

LABEL_ENTITY_DOMAIN = "actions.home_assistant.entity.domain.label"
LABEL_ENTITY_ENTITY = "actions.home_assistant.entity.entity.label"

LABEL_SERVICE_CALL_SERVICE = "actions.home_assistant.service.call_service.label"
LABEL_SERVICE_SERVICE = "actions.home_assistant.service.service.label"
LABEL_SERVICE_NO_DOMAIN = "actions.home_assistant.service.no_domain.label"
LABEL_SERVICE_NO_ENTITY = "actions.home_assistant.service.no_entity.label"
LABEL_SERVICE_NO_SERVICES = "actions.home_assistant.service.no_services.label"
LABEL_SERVICE_PARAMETERS = "actions.home_assistant.service.parameters.label"
LABEL_SERVICE_NO_PARAMETERS = "actions.home_assistant.service.no_parameters.label"

LABEL_ICON_SHOW_ICON = "actions.home_assistant.icon.show_icon.label"
LABEL_ICON_ICON = "actions.home_assistant.icon.icon.label"
LABEL_ICON_COLOR = "actions.home_assistant.icon.color.label"
LABEL_ICON_OPACITY = "actions.home_assistant.icon.opacity.label"
LABEL_ICON_SCALE = "actions.home_assistant.icon.scale.label"
LABEL_ICON_CUSTOM_ICON = "actions.home_assistant.icon.custom_icon.label"
LABEL_ICON_NO_ENTITY = "actions.home_assistant.icon.no_entity.label"

LABEL_TEXT_SHOW_TEXT = "actions.home_assistant.text.show_text.label"
LABEL_TEXT_POSITION = "actions.home_assistant.text.position.label"
LABEL_TEXT_ATTRIBUTE = "actions.home_assistant.text.attribute.label"
LABEL_TEXT_ROUND = "actions.home_assistant.text.round.label"
LABEL_TEXT_ROUND_PRECISION = "actions.home_assistant.text.round_precision.label"
LABEL_TEXT_TEXT_SIZE = "actions.home_assistant.text.text_size.label"
LABEL_TEXT_OUTLINE_SIZE = "actions.home_assistant.text.outline_size.label"
LABEL_TEXT_TEXT_COLOR = "actions.home_assistant.text.text_color.label"
LABEL_TEXT_OUTLINE_COLOR = "actions.home_assistant.text.outline_color.label"
LABEL_TEXT_SHOW_UNIT = "actions.home_assistant.text.show_unit.label"
LABEL_TEXT_SHOW_UNIT_SHORT = "actions.home_assistant.text.show_unit_short.label"
LABEL_TEXT_UNIT_LINE_BREAK = "actions.home_assistant.text.unit_line_break.label"
LABEL_TEXT_UNIT_LINE_BREAK_SHORT = "actions.home_assistant.text.unit_line_break_short.label"
LABEL_TEXT_CUSTOM_TEXT = "actions.home_assistant.text.custom_text.label"
LABEL_TEXT_NO_ENTITY = "actions.home_assistant.text.no_entity.label"

LABEL_SETTINGS_ENTITY = "actions.home_assistant.connection.entity.label"
LABEL_SETTINGS_SERVICE = "actions.home_assistant.connection.service.label"
LABEL_SETTINGS_ACTION = "actions.home_assistant.connection.action.label"
LABEL_SETTINGS_ICON = "actions.home_assistant.connection.icon.label"
LABEL_SETTINGS_TEXT = "actions.home_assistant.connection.text.label"
LABEL_SETTINGS_CONNECTION = "actions.home_assistant.connection.connection.label"

LABEL_CUSTOMIZATION_ICON_TITLE = "actions.home_assistant.customization.icon_title.label"
LABEL_CUSTOMIZATION_TEXT_TITLE = "actions.home_assistant.customization.text_title.label"
LABEL_CUSTOMIZATION_ATTRIBUTE = "actions.home_assistant.customization.attribute.label"
LABEL_CUSTOMIZATION_OPERATOR = "actions.home_assistant.customization.operator.label"
LABEL_CUSTOMIZATION_VALUE = "actions.home_assistant.customization.value.label"
LABEL_CUSTOMIZATION_IF = "actions.home_assistant.customization.if.label"
LABEL_CUSTOMIZATION_CURRENT = "actions.home_assistant.customization.current.label"
LABEL_CUSTOMIZATION_ADD = "actions.home_assistant.customization.add.label"
LABEL_CUSTOMIZATION_UPDATE = "actions.home_assistant.customization.update.label"
LABEL_CUSTOMIZATION_CANCEL = "actions.home_assistant.customization.cancel.label"

LABEL_CUSTOMIZATION_OPERATORS = {
    "==": "actions.home_assistant.customization.equals.label",
    "!=": "actions.home_assistant.customization.not_equals.label",
    "<": "actions.home_assistant.customization.less_than.label",
    "<=": "actions.home_assistant.customization.less_than_equals.label",
    ">": "actions.home_assistant.customization.greater_than.label",
    ">=": "actions.home_assistant.customization.greater_than_equals.label"
}

SETTING_VERSION = "version"
SETTING_UUID = "uuid"

SETTING_ENTITY = "entity"
SETTING_DOMAIN = "domain"
SETTING_ENTITY_DOMAIN = f"{SETTING_ENTITY}.{SETTING_DOMAIN}"
SETTING_ENTITY_ENTITY = f"{SETTING_ENTITY}.{SETTING_ENTITY}"

SETTING_ACTION = "action"
ACTION_PARAMETERS = "parameters"
SETTING_ACTION_ACTION = f"{SETTING_ACTION}.{SETTING_ACTION}"

SETTING_SERVICE = "service"
SETTING_CALL_SERVICE = "call_service"
SETTING_SERVICE_CALL_SERVICE = f"{SETTING_SERVICE}.{SETTING_CALL_SERVICE}"
SETTING_SERVICE_SERVICE = f"{SETTING_SERVICE}.{SETTING_SERVICE}"

SETTING_ICON = "icon"
SETTING_SHOW_ICON = "show_icon"
SETTING_COLOR = "color"
SETTING_SCALE = "scale"
SETTING_OPACITY = "opacity"
SETTING_ICON_SHOW_ICON = f"{SETTING_ICON}.{SETTING_SHOW_ICON}"
SETTING_ICON_ICON = f"{SETTING_ICON}.{SETTING_ICON}"
SETTING_ICON_COLOR = f"{SETTING_ICON}.{SETTING_COLOR}"
SETTING_ICON_SCALE = f"{SETTING_ICON}.{SETTING_SCALE}"
SETTING_ICON_OPACITY = f"{SETTING_ICON}.{SETTING_OPACITY}"

SETTING_TEXT = "text"
SETTING_SHOW_TEXT = "show_text"
SETTING_POSITION = "position"
SETTING_ATTRIBUTE = "attribute"
SETTING_ROUND = "round"
SETTING_ROUND_PRECISION = "round_precision"
SETTING_TEXT_SIZE = "text_size"
SETTING_TEXT_COLOR = "text_color"
SETTING_OUTLINE_SIZE = "outline_size"
SETTING_OUTLINE_COLOR = "outline_color"
SETTING_SHOW_UNIT = "show_unit"
SETTING_UNIT_LINE_BREAK = "unit_line_break"
SETTING_TEXT_SHOW_TEXT = f"{SETTING_TEXT}.{SETTING_SHOW_TEXT}"
SETTING_TEXT_POSITION = f"{SETTING_TEXT}.{SETTING_POSITION}"
SETTING_TEXT_ATTRIBUTE = f"{SETTING_TEXT}.{SETTING_ATTRIBUTE}"
SETTING_TEXT_ROUND = f"{SETTING_TEXT}.{SETTING_ROUND}"
SETTING_TEXT_ROUND_PRECISION = f"{SETTING_TEXT}.{SETTING_ROUND_PRECISION}"
SETTING_TEXT_TEXT_SIZE = f"{SETTING_TEXT}.{SETTING_TEXT_SIZE}"
SETTING_TEXT_TEXT_COLOR = f"{SETTING_TEXT}.{SETTING_TEXT_COLOR}"
SETTING_TEXT_OUTLINE_SIZE = f"{SETTING_TEXT}.{SETTING_OUTLINE_SIZE}"
SETTING_TEXT_OUTLINE_COLOR = f"{SETTING_TEXT}.{SETTING_OUTLINE_COLOR}"
SETTING_TEXT_SHOW_UNIT = f"{SETTING_TEXT}.{SETTING_SHOW_UNIT}"
SETTING_TEXT_UNIT_LINE_BREAK = f"{SETTING_TEXT}.{SETTING_UNIT_LINE_BREAK}"

SETTING_CUSTOMIZATIONS = "customizations"
SETTING_CUSTOMIZATION_ICON = "customization.icon"
SETTING_CUSTOMIZATION_TEXT = "customization.text"

STATE = "state"

CUSTOMIZATION_TYPE_ICON = "icon"
CUSTOMIZATION_TYPE_TEXT = "text"

CUSTOM_ICON_ICON = "icon"
CUSTOM_ICON_COLOR = "color"
CUSTOM_ICON_SCALE = "scale"
CUSTOM_ICON_OPACITY = "opacity"

CUSTOM_TEXT_POSITION = "position"
CUSTOM_TEXT_ATTRIBUTE = "text_attribute"
CUSTOM_TEXT_ROUND = "round"
CUSTOM_TEXT_ROUND_PRECISION = "round_precision"
CUSTOM_TEXT_TEXT_SIZE = "text_size"
CUSTOM_TEXT_TEXT_COLOR = "text_color"
CUSTOM_TEXT_OUTLINE_SIZE = "outline_size"
CUSTOM_TEXT_OUTLINE_COLOR = "outline_color"
CUSTOM_TEXT_SHOW_UNIT = "show_unit"
CUSTOM_TEXT_LINE_BREAK = "line_break"
CUSTOM_TEXT_TEXT_LENGTH = "text_length"
CUSTOM_TEXT_CUSTOM_TEXT = "custom_text"

CUSTOM_CONDITION = "condition"
CUSTOM_ATTRIBUTE = "attribute"
CUSTOM_OPERATOR = "operator"
CUSTOM_VALUE = "value"

ATTRIBUTES = "attributes"
ATTRIBUTE_FRIENDLY_NAME = "friendly_name"
ATTRIBUTE_ICON = "icon"
ATTRIBUTE_UNIT_OF_MEASUREMENT = "unit_of_measurement"
ATTRIBUTE_FIELDS = "fields"

TEXT_POSITION_TOP = "top"
TEXT_POSITION_CENTER = "center"
TEXT_POSITION_BOTTOM = "bottom"

ICON_COLOR_RED = "#ff0000"

ICON_NETWORK_OFF = "network-off"

MDI_SVG_JSON = "assets/mdi-svg.json"

DEFAULT_SERVICE_CALL_SERVICE = False

DEFAULT_ICON_SHOW_ICON = False
DEFAULT_ICON_COLOR = [237, 255, 26, 255]
DEFAULT_ICON_SCALE = 80
DEFAULT_ICON_OPACITY = 100

DEFAULT_TEXT_SHOW_TEXT = False
DEFAULT_TEXT_POSITION = TEXT_POSITION_CENTER
DEFAULT_TEXT_ROUND = False
DEFAULT_TEXT_ROUND_PRECISION = 2
DEFAULT_TEXT_TEXT_SIZE = 20
DEFAULT_TEXT_TEXT_COLOR = [255, 255, 255, 255]
DEFAULT_TEXT_OUTLINE_SIZE = 2
DEFAULT_TEXT_OUTLINE_COLOR = [0, 0, 0, 255]
DEFAULT_TEXT_SHOW_UNIT = False
DEFAULT_TEXT_UNIT_LINE_BREAK = False
DEFAULT_TEXT_ATTRIBUTE = "state"
DEFAULT_TEXT_CUSTOM_TEXT = EMPTY_STRING

ICON_MIN_SCALE = 0
ICON_MAX_SCALE = 100
ICON_MIN_OPACITY = 0
ICON_MAX_OPACITY = 100

TEXT_ROUND_MIN_PRECISION = 0
TEXT_ROUND_MAX_PRECISION = 10
TEXT_TEXT_MIN_SIZE = 0
TEXT_TEXT_MAX_SIZE = 50
TEXT_OUTLINE_MIN_SIZE = 0
TEXT_OUTLINE_MAX_SIZE = 10

CONNECT_CLICKED = "clicked"
CONNECT_TOGGLED = "toggled"
CONNECT_CHANGED = "changed"
CONNECT_ACTIVATE = "activate"
CONNECT_VALUE_CHANGED = "value-changed"
CONNECT_NOTIFY_ACTIVE = "notify::active"
CONNECT_NOTIFY_COLOR_SET = "color-set"

HA_CONNECTED = "connected"
