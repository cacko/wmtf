from typing import Generic, List, TypeVar
from wmtf.wm.models import ReportDay
from rich.console import Console, ConsoleOptions, RenderResult
from .markdown import Markdown

T = TypeVar("T")


class Report(Generic[T]):
    def __init__(
        self,
        wrapped: List[ReportDay],
    ) -> None:
        self.list = wrapped if wrapped else []

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        for day in self.list:
            parts = [f"## {day.day.strftime('%A %d %b')} / {day.total_display}"]
            if not len(day.tasks):
                continue
            for task in day.tasks:
                parts.append(
                    f"- {task.clock_start.strftime('%H:%M')} - {task.clock_end.strftime('%H:%M')} {task.clock.icon.value} **{task.summary}** "
                )
            yield Markdown("\n\n".join(parts))
