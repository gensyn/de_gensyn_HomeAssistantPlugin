from unittest.mock import MagicMock


class ExpanderRow:

    def __init__(self, *args, **kwargs) -> None:
        self.widget = MagicMock()
