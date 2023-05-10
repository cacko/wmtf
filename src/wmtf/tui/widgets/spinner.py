from rich.spinner import Spinner
from textual.widgets import Static

from wmtf.tui.widgets.types import VisibilityMixin


class SpinnerWidget(VisibilityMixin, Static):
    def __init__(self, text="Loading"):
        super().__init__(classes="hidden")
        self._spinner = Spinner("moon", text=text)
        self.update_render = self.set_interval(
            1 / 1, self.update_spinner, pause=True)

    def start(self) -> None:
        self.update_render.resume()

    def stop(self):
        self.update_render.stop()

    def update_spinner(self) -> None:
        self.update(self._spinner)
