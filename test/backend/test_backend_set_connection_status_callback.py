import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend import backend_const
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend


class TestBackendSetConnectionStatusCallback(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_set_callback(self, _):
        instance = HomeAssistantBackend("localhost", "8123", True, True, "abc")

        instance.set_connection_status_callback(lambda: backend_const.FIELD_SUCCESS)

        self.assertEqual(backend_const.FIELD_SUCCESS, instance._connection_status_callback())


if __name__ == '__main__':
    unittest.main()
