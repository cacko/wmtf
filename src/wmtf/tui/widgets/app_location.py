from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from rich.text import Text
from wmtf.config import app_config
from wmtf.wm.models import ClockLocation
from wmtf.tui.theme import Theme


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
        location = ClockLocation(self.location)
        renderable = Text()
        renderable.append(app_config.wm_config.username,
                          Theme.colors.accent_lighten_1)
        renderable.append(
            f" {location.icon.value} {self.location.upper()} ",
            Theme.colors.primary_background_lighten_3,
        )
        return renderable


class AppLocation(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = AppLocationWidget()
        yield self.wdg

    def location(self, val):
        self.wdg.location = val
