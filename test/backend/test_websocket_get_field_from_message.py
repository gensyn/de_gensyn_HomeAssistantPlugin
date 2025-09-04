import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import backend_const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import _get_field_from_message


class TestWebsocketGetFieldFromMessage(unittest.TestCase):

    def test_get_field_from_message_no_message(self):
        result = _get_field_from_message(None, backend_const.FIELD_TYPE)

        self.assertEqual(backend_const.EMPTY_STRING, result)

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.log.error")
    def test_get_field_from_message_error(self, log_mock):
        message = "garbage"
        result = _get_field_from_message(message, backend_const.FIELD_TYPE)

        self.assertEqual(backend_const.EMPTY_STRING, result)
        log_mock.assert_called_once_with(backend_const.ERROR_PARSE.format(message))

    def test_get_field_from_message_success(self):
        state_result = {backend_const.STATE: backend_const.RUNNING}
        message = json.dumps(
            {backend_const.ID: 1, backend_const.FIELD_TYPE: backend_const.FIELD_RESULT, backend_const.FIELD_SUCCESS: True,
             backend_const.FIELD_RESULT: state_result})
        result = _get_field_from_message(message, backend_const.FIELD_RESULT)

        self.assertEqual(state_result, result)

