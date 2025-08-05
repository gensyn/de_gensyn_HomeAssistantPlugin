import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import _get_field_from_message


class TestBackend(unittest.TestCase):

    def test_get_field_from_message_no_message(self):
        result = _get_field_from_message(None, const.FIELD_TYPE)

        self.assertEqual(const.EMPTY_STRING, result)

    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.log.error")
    def test_get_field_from_message_error(self, log_mock):
        message = "garbage"
        result = _get_field_from_message(message, const.FIELD_TYPE)

        self.assertEqual(const.EMPTY_STRING, result)
        log_mock.assert_called_once_with(const.ERROR_PARSE.format(message))

    def test_get_field_from_message_success(self):
        state_result = {const.STATE: const.RUNNING}
        message = json.dumps(
            {const.ID: 1, const.FIELD_TYPE: const.FIELD_RESULT, const.FIELD_SUCCESS: True,
             const.FIELD_RESULT: state_result})
        result = _get_field_from_message(message, const.FIELD_RESULT)

        self.assertEqual(state_result, result)


if __name__ == '__main__':
    unittest.main()
