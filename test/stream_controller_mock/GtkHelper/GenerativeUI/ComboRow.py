class ComboRow:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_selected_item(self):
        pass

    def set_value(self):
        pass

    def _value_changed(self):
        pass

    def set_sensitive(self, _: bool) -> None:
        pass

    def get_item_amount(self) -> int:
        return len(self.args[3])