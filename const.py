"""
Constants for the Home Assistant plugin.
"""

EMPTY_STRING = ""
HOME_ASSISTANT = "Home Assistant"
ERROR = "error"

# BASE
LABEL_BASE_HOST = "actions.base.host.label"
LABEL_BASE_PORT = "actions.base.port.label"
LABEL_BASE_SSL = "actions.base.ssl.label"
LABEL_BASE_VERIFY_CERTIFICATE = "actions.base.verify_certificate.label"
LABEL_BASE_TOKEN = "actions.base.token.label"
LABEL_BASE_SETTINGS_HEADER = "actions.base.settings_header.label"

SETTING_HOST = "host"
SETTING_PORT = "port"
SETTING_SSL = "ssl"
SETTING_VERIFY_CERTIFICATE = "verify_certificate"
SETTING_TOKEN = "token"

# HOME_ASSISTANT_ACTION
CONNECT_BIND = "bind"
CONNECT_CHANGED = "changed"
CONNECT_CLICKED = "clicked"
CONNECT_ACTIVATE = "activate"
CONNECT_TOGGLED = "toggled"
CONNECT_NOTIFY_SELECTED = "notify::selected"
CONNECT_NOTIFY_ACTIVE = "notify::active"
CONNECT_NOTIFY_TEXT = "notify::text"
CONNECT_NOTIFY_COLOR_SET = "color-set"
CONNECT_NOTIFY_ENABLE_EXPANSION = "notify::enable-expansion"

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
LABEL_ICON_CUSTOM_ICONS = "actions.home_assistant.icon.custom_icons.label"
LABEL_ICON_NO_ENTITY = "actions.home_assistant.icon.no_entity.label"

LABEL_TEXT_SHOW_TEXT = "actions.home_assistant.text.show_text.label"
LABEL_TEXT_VALUE = "actions.home_assistant.text.value.label"
LABEL_TEXT_ROUND = "actions.home_assistant.text.round.label"
LABEL_TEXT_ROUND_PRECISION = "actions.home_assistant.text.round_precision.label"
LABEL_TEXT_POSITION = "actions.home_assistant.text.position.label"
LABEL_TEXT_SIZE = "actions.home_assistant.text.size.label"
LABEL_TEXT_ADAPTIVE_SIZE = "actions.home_assistant.text.adaptive_size.label"
LABEL_TEXT_SHOW_UNIT = "actions.home_assistant.text.show_unit.label"
LABEL_TEXT_UNIT_LINE_BREAK = "actions.home_assistant.text.unit_line_break.label"
LABEL_TEXT_NO_ENTITY = "actions.home_assistant.text.no_entity.label"

LABEL_SETTINGS_ENTITY = "actions.home_assistant.settings.entity.label"
LABEL_SETTINGS_SERVICE = "actions.home_assistant.settings.service.label"
LABEL_SETTINGS_ICON = "actions.home_assistant.settings.icon.label"
LABEL_SETTINGS_TEXT = "actions.home_assistant.settings.text.label"
LABEL_SETTINGS_CONNECTION = "actions.home_assistant.settings.connection.label"

LABEL_CUSTOMIZATION_TITLE = "actions.home_assistant.customization.title.label"
LABEL_CUSTOMIZATION_ATTRIBUTE = "actions.home_assistant.customization.attribute.label"
LABEL_CUSTOMIZATION_OPERATOR = "actions.home_assistant.customization.operator.label"
LABEL_CUSTOMIZATION_VALUE = "actions.home_assistant.customization.value.label"
LABEL_CUSTOMIZATION_IF = "actions.home_assistant.customization.if.label"
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


SETTING_ENTITY_DOMAIN = "entity.domain"
SETTING_ENTITY_ENTITY = "entity.entity"

SETTING_SERVICE_CALL_SERVICE = "service.call_service"
SETTING_SERVICE_SERVICE = "service.service"
SETTING_SERVICE_PARAMETERS = "service.service_parameters"

SETTING_ICON_SHOW_ICON = "icon.show_icon"
SETTING_ICON_ICON = "icon.icon"
SETTING_ICON_COLOR = "icon.color"
SETTING_ICON_OPACITY = "icon.opacity"
SETTING_ICON_SCALE = "icon.scale"

SETTING_TEXT_SHOW_TEXT = "text.show_text"
SETTING_TEXT_ATTRIBUTE = "text.attribute"
SETTING_TEXT_ROUND = "text.round"
SETTING_TEXT_ROUND_PRECISION = "text.round_precision"
SETTING_TEXT_POSITION = "text.position"
SETTING_TEXT_ADAPTIVE_SIZE = "text.adaptive_size"
SETTING_TEXT_SIZE = "text.size"
SETTING_TEXT_SHOW_UNIT = "text.show_unit"
SETTING_TEXT_UNIT_LINE_BREAK = "text.unit_line_break"

SETTING_CONNECTION_STATUS = "actions.home_assistant.connection.connection_status.label"

SETTING_CUSTOMIZATION_ICONS = "customization.icons"

STATE = "state"
STATE_ON = "on"
STATE_HOME = "home"

CUSTOM_ICON_ICON = "icon"
CUSTOM_ICON_COLOR = "color"
CUSTOM_ICON_SCALE = "scale"
CUSTOM_ICON_OPACITY = "opacity"
CUSTOM_ICON_OPERATOR = "operator"
CUSTOM_ICON_VALUE = "value"
CUSTOM_ICON_ATTRIBUTE = "attribute"

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
DEFAULT_ICON_COLOR = [0.93, 1, 0.1]
DEFAULT_ICON_SCALE = 80
DEFAULT_ICON_OPACITY = 100

DEFAULT_TEXT_SHOW_TEXT = False
DEFAULT_TEXT_ROUND = False
DEFAULT_TEXT_ROUND_PRECISION = 2
DEFAULT_TEXT_POSITION = TEXT_POSITION_CENTER
DEFAULT_TEXT_ADAPTIVE_SIZE = True
DEFAULT_TEXT_SIZE = 20
DEFAULT_TEXT_SHOW_UNIT = False
DEFAULT_TEXT_UNIT_LINE_BREAK = False

CONNECTED = "Connected"
CONNECTING = "Connecting"
DISCONNECTING = "Disconnecting"
NOT_CONNECTED = "Not connected"
AUTHENTICATING = "Authenticating"
WAITING_FOR_RETRY = "Waiting for retry"

HA_CONNECTED = "connected"