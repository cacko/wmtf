from rich.spinner import Spinner
from textual.widgets import Static


class SpinnerWidget(Static):
    def __init__(self):
        super().__init__("")
        self._spinner = Spinner("moon")

    def on_mount(self) -> None:
        self.update_render = self.set_interval(1 / 60, self.update_spinner)

    def update_spinner(self) -> None:
        self.update(self._spinner)
