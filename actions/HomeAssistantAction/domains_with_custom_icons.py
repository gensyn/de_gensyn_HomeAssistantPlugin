"""
Module to define custom icons for services.
"""
from typing import Dict

DOMAINS_WITH_SERVICE_ICONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "media_player": {
        "media_play_pause": {
            "playing": "pause",
            "default": "play",
        },
        "media_stop": {
            "default": "stop",
        },
        "volume_up": {
            "default": "volume-plus"
        },
        "volume_down": {
            "default": "volume-minus"
        },
        "media_next_track": {
            "default": "skip-next"
        },
        "media_previous_track": {
            "default": "skip-previous"
        }
    }
}
