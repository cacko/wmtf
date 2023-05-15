from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Optional
import arrow
from wmtf.tui.theme import Theme
from humanize import naturaldelta
from pydantic import BaseModel
import re

RECENT_PATTERN = re.compile(r"RECENT<br>(\d+)(h|m|d)")


def extract_recent(text: str) -> Optional[tuple[int, str]]:
    if matches := RECENT_PATTERN.search(text):
        return (int(matches[1]), str(matches[2]))
    return None


class TimeDeltaUnit(StrEnum):
    DAYS = "d"
    HOURS = "h"
    MINUTES = "m"


class ClockIcon(StrEnum):
    HOME = "🏠"
    OFFICE = "🏢"
    OFF = ""


class ClockLocation(StrEnum):
    HOME = "home"
    OFFICE = "office"
    OFF = ""

    @property
    def icon(self) -> ClockIcon:
        match self:
            case self.HOME:
                return ClockIcon.HOME
            case self.OFFICE:
                return ClockIcon.OFFICE
            case _:
                return ClockIcon.OFF


class TimeDelta(BaseModel):
    number: float
    unit: TimeDeltaUnit


class ReportTask(BaseModel):
    id: int
    clock: ClockLocation
    clock_time: timedelta
    clock_start: datetime
    clock_end: datetime
    summary: str


class ReportDay(BaseModel):
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


class TaskInfo(BaseModel):
    id: int
    summary: str
    clock_id: int
    clock: ClockLocation
    clock_start: Optional[datetime] = None
    estimate: Optional[timedelta] = None
    estimate_used: Optional[float] = None
    task_updated: Optional[timedelta] = None
    group: Optional[str] = None

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


class TaskComment(BaseModel):
    author: str
    comment: str
    timestamp: datetime

    @property
    def timestamp_display(self):
        return arrow.get(self.timestamp).humanize()


class Task(BaseModel):
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

    @property
    def created(self) -> datetime:

        if recent := extract_recent(self.create):
            p, u = recent[0], TimeDeltaUnit(recent[1])
            match u:
                case TimeDeltaUnit.DAYS:
                    return datetime.now() - timedelta(days=p)
                case TimeDeltaUnit.HOURS:
                    return datetime.now() - timedelta(hours=p)
                case TimeDeltaUnit.MINUTES:
                    return datetime.now() - timedelta(minutes=p)
            return datetime.now()

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
