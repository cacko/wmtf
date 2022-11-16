from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from rich.text import Text
from wmtf.config import app_config


class AppUserWidget(Static):
    def on_mount(self) -> None:
        self.update(self.render())

    def render(self):
        return Text.from_markup(f"username: [yellow]{app_config.wm_config.username}[/]")


class AppUser(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = AppUserWidget()
        yield self.wdg
