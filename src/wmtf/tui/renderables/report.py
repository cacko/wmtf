from typing import Generic, List, TypeVar
from wmtf.wm.models import ReportDay
from .markdown import Markdown
from typing import Optional

T = TypeVar("T")


class Days(Generic[T]):
    def __init__(
        self, wrapped: List[ReportDay], today_total_display: Optional[str] = None
    ) -> None:
        self.list = wrapped if wrapped else []
        self.running_total = today_total_display

    def __rich__(self) -> Markdown:
        parts = []
        for day in reversed(self.list):
            if day.is_weekend:
                continue
            total_display = (
                self.running_total
                if day.is_today and self.running_total
                else day.total_display
            )
            parts.append(f"## {day.day.strftime('%A %d %b').upper()} / {total_display}")
            if not len(day.tasks):
                parts.append("- Nothing clocked.")
            for task in day.tasks:
                parts.append(
                    f"- {task.clock_start.strftime('%H:%M')} - {task.clock_end.strftime('%H:%M')} {task.clock.icon.value} **{task.summary}** "
                )
        return Markdown("\n\n".join(parts))
