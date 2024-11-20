"""
Entry point for StreamController to load the plugin.
"""
import sys
from pathlib import Path
from typing import Dict, Any

absolute_plugin_path = str(Path(__file__).parent.parent.absolute())

sys.path.insert(0, absolute_plugin_path)

from de_gensyn_HomeAssistantPlugin import const

from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase

from de_gensyn_HomeAssistantPlugin.actions.HomeAssistantAction.home_asistant_action import \
    HomeAssistantAction
from de_gensyn_HomeAssistantPlugin.backend.home_assistant import HomeAssistantBackend


class HomeAssistant(PluginBase):
    """
    The plugin class to be loaded by Stream Controller.
    """

    def __init__(self):
        super().__init__()

        self.home_assistant_action_holder = ActionHolder(
            plugin_base=self,
            action_base=HomeAssistantAction,
            action_id="de_gensyn_HomeAssistantPlugin::HomeAssistantAction",
            action_name=const.HOME_ASSISTANT,
        )
        self.add_action_holder(self.home_assistant_action_holder)

        self.register(
            plugin_name=const.HOME_ASSISTANT,
            github_repo="https://github.com/gensyn/de_gensyn_HomeAssistantPlugin",
            plugin_version="0.9.3-beta",
            app_version="1.5.0-beta"
        )

        settings = self.get_settings()
        host = settings.get(const.SETTING_HOST, const.EMPTY_STRING)
        port = settings.get(const.SETTING_PORT, const.EMPTY_STRING)
        ssl = settings.get(const.SETTING_SSL, True)
        token = settings.get(const.SETTING_TOKEN, const.EMPTY_STRING)

        self.backend = HomeAssistantBackend()
        self.backend.set_host(host)
        self.backend.set_port(port)
        self.backend.set_ssl(ssl)
        self.backend.set_token(token)

    def set_settings(self, settings: Dict[str, Any]):
        """
        Saves the settings to the disk.
        """
        super().set_settings(settings)

        host = settings.get(const.SETTING_HOST, const.EMPTY_STRING)
        port = settings.get(const.SETTING_PORT, const.EMPTY_STRING)
        ssl = settings.get(const.SETTING_SSL, True)
        token = settings.get(const.SETTING_TOKEN, const.EMPTY_STRING)

        self.backend.set_host(host)
        self.backend.set_port(port)
        self.backend.set_ssl(ssl)
        self.backend.set_token(token)
