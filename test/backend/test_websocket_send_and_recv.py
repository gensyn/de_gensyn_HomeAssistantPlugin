import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import backend_const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketSendAndRecv(unittest.TestCase):

    @patch.object(HomeAssistantWebsocket, 'send')
    def test_send_and_recv_not_connected(self, send_mock):
        instance = HomeAssistantWebsocket(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, None, None, None)
        success, result, error = instance.send_and_recv(backend_const.GET_CONFIG)
        self.assertFalse(success)
        self.assertEqual(backend_const.EMPTY_STRING, result)
        self.assertEqual(backend_const.EMPTY_STRING, error)

        send_mock.assert_not_called()

    @patch.object(HomeAssistantWebsocket, 'send')
    def test_send_and_recv_success(self, send_mock):
        state_result = {backend_const.STATE: backend_const.RUNNING}

        recv_mock = Mock()
        recv_mock.return_value = json.dumps(
            {backend_const.ID: 1, backend_const.FIELD_TYPE: backend_const.FIELD_RESULT, backend_const.FIELD_SUCCESS: True,
             backend_const.FIELD_RESULT: state_result})

        sock_mock = Mock()
        sock_mock.recv = recv_mock

        instance = HomeAssistantWebsocket(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, None, None, None)
        instance.sock = sock_mock
        instance.connected = True
        success, result, error = instance.send_and_recv(backend_const.GET_CONFIG)
        self.assertTrue(success)
        self.assertEqual(state_result, result)
        self.assertEqual(backend_const.EMPTY_STRING, error)

        send_mock.assert_called_once_with({backend_const.ID: 1, backend_const.FIELD_TYPE: backend_const.GET_CONFIG}, True)


if __name__ == '__main__':
    unittest.main()
