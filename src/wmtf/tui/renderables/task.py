from wmtf.wm.models import Task as TaskModel
from .markdown import Markdown
from wmtf.wm.html.parser import textual_links
from rich.console import RenderResult, Console, ConsoleOptions
from textual.widgets import Static


class Task:
    def __init__(
        self,
        wrapped: TaskModel,
    ) -> None:
        self.task = wrapped

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield Static(self.task.summary, classes="task-summary h1").renderable
        yield Static(
            textual_links(self.task.description, "open_browser"),
            classes="task-description",
        ).renderable

        if self.task.comments:
            parts = ["## Comments"]
            for c in self.task.comments:
                parts.append(
                    f"> **{c.author}**\n>\n> {textual_links(c.comment, 'open_browser')}"
                )
            yield Markdown("\n\n".join(parts))
