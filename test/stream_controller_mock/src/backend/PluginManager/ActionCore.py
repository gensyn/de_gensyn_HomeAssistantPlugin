from unittest.mock import Mock


class ActionCore:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.plugin_base = Mock()
        self.plugin_base.locale_manager = Mock()
        self.plugin_base.backend = Mock()
        self.plugin_base.add_tracked_entity = Mock()
        pass
