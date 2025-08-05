import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import const


class TestBackend(unittest.TestCase):

    def test_get_entities_domain_empty(self):
        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        result = instance.get_entities(const.EMPTY_STRING)

        self.assertEqual([], result)

    def test_get_entities_already_loaded(self):
        entities = {
            "light": {"light.living_room": {const.STATE: "on", const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, const.ACTIONS: {"abc": "123"}, const.SUBSCRIPTION_ID: 2}},
            "sensor": {
                "sensor.temperature": {const.STATE: "23", const.ATTRIBUTES: {"unit_of_measurement": "°C", "friendly_name": "Temperature Sensor"}, const.ACTIONS: {"cba": "321"}, const.SUBSCRIPTION_ID: 3},
                "sensor.humidity": {const.STATE: "45", const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}, const.ACTIONS: {"bac": "213"}, const.SUBSCRIPTION_ID: 4}
            }
        }

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        instance._entities = entities
        result = instance.get_entities("light")
        self.assertEqual(["light.living_room"], result)
        result = instance.get_entities("sensor")
        self.assertEqual(["sensor.temperature", "sensor.humidity"], result)

    @patch.object(HomeAssistantBackend, '_load_entities')
    def test_get_entities_load_entities(self, load_entities_mock):
        entities = {
            "light": {"light.living_room": {const.STATE: "on", const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, const.ACTIONS: {"abc": "123"}, const.SUBSCRIPTION_ID: 2}},
            "sensor": {
                "sensor.temperature": {const.STATE: "23", const.ATTRIBUTES: {"unit_of_measurement": "°C", "friendly_name": "Temperature Sensor"}, const.ACTIONS: {"cba": "321"}, const.SUBSCRIPTION_ID: 3},
                "sensor.humidity": {const.STATE: "45", const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}, const.ACTIONS: {"bac": "213"}, const.SUBSCRIPTION_ID: 4}
            }
        }

        load_entities_mock.side_effect = lambda: setattr(instance, '_entities', entities)

        instance = HomeAssistantBackend(const.EMPTY_STRING, const.EMPTY_STRING, True, True, const.EMPTY_STRING)
        result = instance.get_entities("light")
        self.assertEqual(["light.living_room"], result)
        result = instance.get_entities("sensor")
        self.assertEqual(["sensor.temperature", "sensor.humidity"], result)


if __name__ == '__main__':
    unittest.main()
