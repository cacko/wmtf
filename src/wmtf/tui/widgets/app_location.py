from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from rich.text import Text
from wmtf.config import app_config


class AppLocationWidget(Static):

    location = reactive(app_config.wm_config.location)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def watch_location(self, old_location: str, new_location: str) -> None:
        if new_location != old_location:
            app_config.set("wm.location", new_location)
            self.location = new_location

    def on_mount(self) -> None:
        self.update(self.render())

    def render(self):
        return Text(self.location)


class AppLocation(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = AppLocationWidget(expand=True)
        yield self.wdg

    def location(self, val):
        self.wdg.location = val
