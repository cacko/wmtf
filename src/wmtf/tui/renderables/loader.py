from rich.spinner import Spinner
from rich.console import RenderResult, Console, ConsoleOptions
from rich.text import Text


class Loader:
    def __init__(
        self,
        text: str,
    ) -> None:
        self.text = text
        self._spinner = Spinner("moon")
        # self.update_render = self.set_interval(1 / 60, self.update_spinner)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield self._spinner
        yield Text(self.text)