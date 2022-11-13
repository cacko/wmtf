from typing import Generic, TypeVar
from wmtf.wm.models import Task as TaskModel
from rich.panel import Panel
from rich.markdown import Markdown
from rich.console import Console, ConsoleOptions, RenderResult

T = TypeVar("T")


class Task(Generic[T]):
    def __init__(
        self,
        wrapped: TaskModel,
    ) -> None:
        self.task = wrapped

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        parts = [f"# {self.task.summary}", self.task.description, "---"]
        if self.task.comments:
            for c in self.task.comments:
                parts.append(f"> **{c.author}**\n>\n> {c.comment}")
        yield Markdown("\n\n".join(parts)) 
