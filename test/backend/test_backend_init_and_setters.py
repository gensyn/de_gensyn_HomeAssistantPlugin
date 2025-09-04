import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend


class TestBackendInitAndSetters(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_init_and_setters(self, _):
        instance = HomeAssistantBackend("localhost", "8123", True, True, "abc")

        self.assertEqual("localhost", instance._host)
        self.assertEqual("8123", instance._port)
        self.assertTrue(instance._ssl)
        self.assertTrue(instance._verify_certificate)
        self.assertEqual("abc", instance._token)

        instance.set_host("hostlocal")
        instance.set_port("3218")
        instance.set_ssl(False)
        instance.set_verify_certificate(False)
        instance.set_token("cba")

        self.assertEqual("hostlocal", instance._host)
        self.assertEqual("3218", instance._port)
        self.assertFalse(instance._ssl)
        self.assertFalse(instance._verify_certificate)
        self.assertEqual("cba", instance._token)

