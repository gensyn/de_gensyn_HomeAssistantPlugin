import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from de_gensyn_HomeAssistantPlugin.backend import backend_const


class TestBackendOnEventMessage(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_on_event_message_no_new_state(self, _):
        wrong_mock = Mock()
        right_mock = Mock()

        entities = {
            "domain1": {
                "domain1.entity1": {
                    backend_const.ACTIONS: {
                        wrong_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "1.3"
                },
                "domain1.entity2": {
                    backend_const.ACTIONS: {
                        right_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "2.3"
                }
            },
            "domain2": {
                "domain2.entity3": {
                    backend_const.ACTIONS: {
                        wrong_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "3.3"
                }
            }
        }

        message = {
            backend_const.FIELD_EVENT: {
                backend_const.VARIABLES: {
                    backend_const.TRIGGER: {
                        backend_const.FROM_STATE: {
                            backend_const.ENTITY_ID: "domain1.entity2"
                        },
                    }
                }
            }
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities
        instance._on_event_message(message)

        wrong_mock.assert_not_called()
        right_mock.assert_called_once()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected')
    @patch("de_gensyn_HomeAssistantPlugin.backend.home_assistant_backend.log.warning")
    def test_on_event_message_not_subscribed(self, log_mock, is_connected_mock, _):
        wrong_mock = Mock()

        entities = {
            "domain1": {
                "domain1.entity1": {
                    backend_const.ACTIONS: {
                        wrong_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "1.3"
                },
                "domain1.entity2": {
                    backend_const.ACTIONS: set(),
                    backend_const.SUBSCRIPTION_ID: -1
                }
            },
            "domain2": {
                "domain2.entity3": {
                    backend_const.ACTIONS: {
                        wrong_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "3.3"
                }
            }
        }

        message = {
            backend_const.FIELD_EVENT: {
                backend_const.VARIABLES: {
                    backend_const.TRIGGER: {
                        backend_const.TO_STATE: {
                            backend_const.ENTITY_ID: "domain1.entity2"
                        },
                    }
                }
            }
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities
        instance._on_event_message(message)

        wrong_mock.assert_not_called()
        is_connected_mock.assert_called_once()
        log_mock.assert_called_once_with(backend_const.WARNING_NOT_SUBSCRIBED.format("domain1.entity2"))

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_on_event_message_success(self, is_connected_mock, _):
        wrong_mock = Mock()
        right_mock = Mock()

        entities = {
            "domain1": {
                "domain1.entity1": {
                    backend_const.ACTIONS: {
                        wrong_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "1.3"
                },
                "domain1.entity2": {
                    backend_const.ACTIONS: {
                        right_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "2.3"
                }
            },
            "domain2": {
                "domain2.entity3": {
                    backend_const.ACTIONS: {
                        wrong_mock
                    },
                    backend_const.SUBSCRIPTION_ID: "3.3"
                }
            }
        }

        attributes = {
            "brightness": 5,
            "transition": "10"
        }

        message = {
            backend_const.FIELD_EVENT: {
                backend_const.VARIABLES: {
                    backend_const.TRIGGER: {
                        backend_const.TO_STATE: {
                            backend_const.ENTITY_ID: "domain1.entity2",
                            backend_const.STATE: backend_const.OFF,
                            backend_const.ATTRIBUTES: attributes
                        },
                    }
                }
            }
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities
        instance._on_event_message(message)

        wrong_mock.assert_not_called()
        is_connected_mock.assert_called_once()
        right_mock.assert_called_once_with({
            backend_const.STATE: backend_const.OFF,
            backend_const.ATTRIBUTES: attributes,
            backend_const.HA_CONNECTED: True,
        })

