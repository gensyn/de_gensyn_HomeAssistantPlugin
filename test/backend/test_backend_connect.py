import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendConnect(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'disconnect')
    def test_connect_no_host(self, disconnect_mock):
        connection_status_callback_mock = Mock()

        with patch.object(HomeAssistantBackend, "connect"):
            # connect is called in the backend_constructor, so we patch it to only call it once
            instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._connection_status_callback = connection_status_callback_mock

        instance.connect()

        disconnect_mock.assert_called_once()
        connection_status_callback_mock.assert_not_called()

    @patch.object(HomeAssistantBackend, 'disconnect')
    def test_connect_no_token(self, disconnect_mock):
        connection_status_callback_mock = Mock()

        with patch.object(HomeAssistantBackend, "connect"):
            # connect is called in the backend_constructor, so we patch it to only call it once
            instance = HomeAssistantBackend("localhost", backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._connection_status_callback = connection_status_callback_mock
        instance.connect()

        disconnect_mock.assert_called_once()
        connection_status_callback_mock.assert_not_called()

    @patch.object(HomeAssistantBackend, 'disconnect')
    def test_connect_no_port(self, disconnect_mock):
        connection_status_callback_mock = Mock()

        with patch.object(HomeAssistantBackend, "connect"):
            # connect is called in the backend_constructor, so we patch it to only call it once
            instance = HomeAssistantBackend("localhost", backend_const.EMPTY_STRING, True, True, "abc")
        instance._connection_status_callback = connection_status_callback_mock
        instance.connect()

        disconnect_mock.assert_called_once()
        connection_status_callback_mock.assert_not_called()

    @patch.object(HomeAssistantBackend, 'disconnect')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.HomeAssistantWebsocket")
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.Thread")
    def test_connect_success(self, thread_mock, websocket_mock, disconnect_mock):
        host = "localhost"
        port = "8123"
        token = "abc"

        connection_status_callback_mock = Mock()

        thread_start_mock = Mock()

        thread_init_mock = Mock()
        thread_init_mock.start = thread_start_mock

        thread_mock.return_value = thread_init_mock

        with patch.object(HomeAssistantBackend, "connect"):
            # connect is called in the backend_constructor, so we patch it to only call it once
            instance = HomeAssistantBackend(host, port, True, True, token)
        instance._connection_status_callback = connection_status_callback_mock
        instance.connect()

        disconnect_mock.assert_called_once()
        connection_status_callback_mock.assert_called_with(backend_const.CONNECTING)
        websocket_mock.assert_called_once_with(url=f"wss://{host}:{port}{backend_const.HASS_WEBSOCKET_API}", token=token,
                                               verify_certificate=True, on_event_message=instance._on_event_message,
                                               on_connected=instance._on_connect, on_close=instance._on_disconnect)
        thread_mock.assert_called_once_with(target=instance._websocket.run_forever, daemon=True)
        thread_start_mock.assert_called_once()

