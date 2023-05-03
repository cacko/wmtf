from typing import Generic, List, TypeVar
from wmtf.wm.models import ReportDay
from .markdown import Markdown

T = TypeVar("T")


class Days(Generic[T]):
    def __init__(
        self, wrapped: List[ReportDay]
    ) -> None:
        self.list = wrapped if wrapped else []

    def __rich__(self) -> Markdown:
        parts = []
        for day in reversed(self.list):
            if day.is_weekend:
                continue
            if not day.is_today:
                parts.append(
                    f"# {day.day.strftime('%A %d %b').upper()}"
                    f" / {day.total_display}"
                )
            if not len(day.tasks):
                parts.append("- Nothing clocked.")
            for task in day.tasks:
                parts.append(
                    f"- {task.clock_start.strftime('%H:%M')} - "
                    f"{task.clock_end.strftime('%H:%M')} "
                    f"{task.clock.icon.value} **{task.summary}** "
                )
        return Markdown("\n\n".join(parts))
