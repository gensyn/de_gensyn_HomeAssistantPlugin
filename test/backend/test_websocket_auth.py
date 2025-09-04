import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock, call

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import backend_const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketAuth(unittest.TestCase):

    @patch.object(HomeAssistantWebsocket, 'send')
    @patch.object(HomeAssistantWebsocket, 'send_and_recv')
    @patch('loguru.logger.error')
    def test_auth_auth_nok(self, log_mock, send_and_recv_mock, send_mock):
        auth_nok = "{\"type\": \"auth_nok\"}"
        token = "abc"

        sock_mock = Mock()
        sock_mock.recv = Mock(return_value=auth_nok)

        instance = HomeAssistantWebsocket(backend_const.EMPTY_STRING, token, True, None, None, None)
        instance.sock = sock_mock
        instance._auth()

        send_mock.assert_called_once_with({backend_const.FIELD_TYPE: backend_const.AUTH, backend_const.ACCESS_TOKEN: token}, check_connected=False)
        log_mock.assert_called_once_with(backend_const.AUTH_ERROR)
        send_and_recv_mock.assert_not_called()

    @patch.object(HomeAssistantWebsocket, 'send')
    @patch.object(HomeAssistantWebsocket, 'send_and_recv')
    @patch('loguru.logger.error')
    @patch('loguru.logger.info')
    @patch('de_gensyn_HomeAssistantPlugin.backend.home_assistant_websocket.sleep')
    def test_auth_auth_ok_in_third_try(self, sleep_mock, log_info_mock, log_error_mock, send_and_recv_mock, send_mock):
        auth_ok = "{\"type\": \"auth_ok\"}"
        token = "abc"

        sock_mock = Mock()
        sock_mock.recv = Mock(return_value=auth_ok)

        send_and_recv_mock.side_effect = [(False, None, None), (True, {}, None), (True, {backend_const.STATE: backend_const.RUNNING}, None)]

        on_connected_mock = Mock()

        instance = HomeAssistantWebsocket(backend_const.EMPTY_STRING, token, True, None, on_connected_mock, None)
        instance.sock = sock_mock

        self.assertFalse(instance.connected)

        instance._auth()

        send_mock.assert_called_once_with({backend_const.FIELD_TYPE: backend_const.AUTH, backend_const.ACCESS_TOKEN: token}, check_connected=False)
        log_error_mock.assert_not_called()
        self.assertEqual(3, send_and_recv_mock.call_count)
        send_and_recv_mock.assert_has_calls([call(backend_const.GET_CONFIG, check_connected=False)] * 3)
        self.assertEqual(2, log_info_mock.call_count)
        log_info_mock.assert_has_calls([call(backend_const.ERROR_NOT_STARTED)] * 2)
        self.assertEqual(2, sleep_mock.call_count)
        sleep_mock.assert_has_calls([call(backend_const.RECONNECT_INTERVAL)] * 2)
        self.assertTrue(instance.connected)
        on_connected_mock.assert_called_once()

