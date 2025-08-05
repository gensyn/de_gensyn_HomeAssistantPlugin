import sys
import unittest
from pathlib import Path

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketCreateMessage(unittest.TestCase):

    def test_create_message(self):
        message_id = 15
        instance = HomeAssistantWebsocket(const.EMPTY_STRING, const.EMPTY_STRING, True, None, None, None)
        instance._message_id = message_id
        result = instance.create_message(const.GET_CONFIG)
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertEqual(message_id + 1, result[const.ID])
        self.assertEqual(const.GET_CONFIG, result[const.FIELD_TYPE])


if __name__ == '__main__':
    unittest.main()
