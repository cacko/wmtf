from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional
import arrow

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
        return self.day.weekday() in [5,6]


@dataclass
class TaskInfo:
    id: int
    summary: str
    clock_id: int
    clock: ClockLocation
    clock_start: Optional[datetime] = None

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

    @property
    def created(self) -> datetime:
        parts = [TimeDelta(number=float(x[:-1]), unit=TimeDeltaUnit(x[-1])) for x in self.create.split(" ")]
        units = {}
        for part in parts:
            match part.unit:
                case TimeDeltaUnit.DAYS:
                    units['days'] = part.number
                case TimeDeltaUnit.HOURS:
                    units["hours"] = part.number
                case TimeDeltaUnit.MINUTES:
                    units['minues'] = part.number
        td = timedelta(**units)
        return datetime.now() - td

    @property
    def age(self) -> str:
        return arrow.get(self.created).humanize(arrow.now())

    
