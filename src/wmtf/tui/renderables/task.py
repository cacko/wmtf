from wmtf.wm.models import Task as TaskModel
from rich.markdown import Markdown
from rich.console import Console, ConsoleOptions, RenderResult, ConsoleRenderable


class Task(ConsoleRenderable):
    def __init__(
        self,
        wrapped: TaskModel,
    ) -> None:
        self.task = wrapped

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        parts = [f"## {self.task.summary}", self.task.description]
        if self.task.comments:
            parts.append("## Comments")
            for c in self.task.comments:
                parts.append(f"> **{c.author}**\n>\n> {c.comment}")
        yield Markdown("\n\n".join(parts))
