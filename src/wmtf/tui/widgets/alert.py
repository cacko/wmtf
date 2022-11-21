from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from rich.text import Text
from wmtf.tui.widgets.types import VisibilityMixin


class AlertWidget(Static):

    message = reactive("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        self.update(self.render())

    def render(self):
        return Text(self.message)


class Alert(VisibilityMixin, Widget):
    def compose(self) -> ComposeResult:
        self.wdg = Alert()
        yield self.wdg

    def message(self, val):
        self.wdg.message = val
