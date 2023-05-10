from textual.app import ComposeResult
from textual.widgets import Label

from wmtf.tui.widgets.types import Focusable


class Users(Focusable):

    def compose(self) -> ComposeResult:
        yield Label("shit")
