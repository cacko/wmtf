from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional, Any
import arrow
from wmtf.tui.theme import Theme
from humanize import naturaldelta


class TimeDeltaUnit(Enum):
    DAYS = "d"
    HOURS = "h"
    MINUTES = "m"


class ClockIcon(Enum):
    HOME = "🏠"
    OFFICE = "🏢"
    OFF = ""


class ClockLocation(Enum):
    HOME = "home"
    OFFICE = "office"
    OFF = "off"

    @property
    def icon(self) -> ClockIcon:
        match self:
            case self.HOME:
                return ClockIcon.HOME
            case self.OFFICE:
                return ClockIcon.OFFICE
            case _:
                return ClockIcon.OFF


@dataclass
class TimeDelta:
    number: float
    unit: TimeDeltaUnit


@dataclass
class ReportTask:
    id: int
    clock: ClockLocation
    clock_time: timedelta
    clock_start: datetime
    clock_end: datetime
    summary: str

    def dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "clock": self.clock.value,
            "clock_time": self.clock_time.seconds,
            "clock_start": self.clock_start.isoformat(),
            "clock_end": self.clock_end.isoformat(),
            "summary": self.summary,
        }


@dataclass
class ReportDay:
    day: date
    total_work: timedelta
    tasks: list[ReportTask]

    @property
    def total_display(self) -> str:
        return ":".join(str(self.total_work).split(":")[:2])

    @property
    def is_today(self) -> bool:
        return datetime.now().date() == self.day

    @property
    def is_weekend(self) -> bool:
        return self.day.weekday() in [5, 6]

    def dict(self) -> dict[str, Any]:
        return {
            "day": self.day.isoformat(),
            "total_work": self.total_work.seconds,
            "tasks": [t.dict() for t in self.tasks],
        }


@dataclass
class TaskInfo:
    id: int
    summary: str
    clock_id: int
    clock: ClockLocation
    clock_start: Optional[datetime] = None
    estimate: Optional[timedelta] = None
    estimate_used: Optional[float] = None

    def dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "clock_id": self.clock_id,
            "clock": self.clock.value,
            "clock_start": self.clock_start.isoformat() if self.clock_start else None,
            "estimate": self.estimate.seconds if self.estimate else None,
            "estimate_user": self.estimate_used if self.estimate_used else None,
        }

    @property
    def isActive(self):
        return self.clock in [ClockLocation.HOME, ClockLocation.OFFICE]

    @property
    def work_display(self) -> str:
        if not self.isActive:
            return ""
        if not self.clock_start:
            return ""
        df = datetime.now() - self.clock_start
        return str(df).split(".")[0]

    def __str__(self) -> str:
        return self.summary


@dataclass
class TaskComment:
    author: str
    comment: str
    timestamp: datetime

    @property
    def timestamp_display(self):
        return arrow.get(self.timestamp).humanize()

    def dict(self) -> dict[str, Any]:
        return {
            "author": self.author,
            "comment": self.comment,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Task:
    id: int
    summary: str
    description: str
    assignee: str
    group: str
    priority: int
    value: str
    create: str
    comments: Optional[list[TaskComment]] = None
    estimate: Optional[timedelta] = None
    estimate_used: Optional[float] = None

    def dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "assignee": self.assignee,
            "group": self.group,
            "priority": self.priority,
            "value": self.value,
            "created": self.created.isoformat(),
            "comments": [c.dict() for c in self.comments] if self.comments else [],
            "estimate": self.estimate.seconds if self.estimate else None,
            "estimate_used": self.estimate_used if self.estimate_used else None,
        }

    @property
    def created(self) -> datetime:
        parts = [
            TimeDelta(number=float(x[:-1]), unit=TimeDeltaUnit(x[-1]))
            for x in self.create.split(" ")
        ]
        units = {}
        for part in parts:
            match part.unit:
                case TimeDeltaUnit.DAYS:
                    units["days"] = part.number
                case TimeDeltaUnit.HOURS:
                    units["hours"] = part.number
                case TimeDeltaUnit.MINUTES:
                    units["minues"] = part.number
        td = timedelta(**units)
        return datetime.now() - td

    @property
    def age(self) -> str:
        return arrow.get(self.created).humanize(arrow.now())

    @property
    def estimate_color(self) -> str:
        try:
            assert self.estimate_used
            stage = self.estimate_used + (33 - self.estimate_used) % 33
            match (stage):
                case 33:
                    return Theme.colors.text
                case 66:
                    return Theme.colors.warning
                case 99:
                    return Theme.colors.warning_lighten_2
                case _:
                    return Theme.colors.error_lighten_3
        except AssertionError:
            return Theme.colors.text

    @property
    def estimateDisplay(self) -> str:
        try:
            assert self.estimate
            return naturaldelta(self.estimate)
        except AssertionError:
            return "N/A"
