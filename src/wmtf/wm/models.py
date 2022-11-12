from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional

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


@dataclass
class TaskInfo:
    id: int
    summary: str
    clock_id: int
    clock: ClockLocation

    @property
    def isActive(self):
        return self.clock in [ClockLocation.HOME, ClockLocation.OFFICE]
    
    def __str__(self) -> str:
        return self.summary

@dataclass
class TaskComment:
    date: str
    author: str
    comment: str

@dataclass
class Task:
    id: int
    summary: str
    description: str
    assignee: str
    comments: Optional[list[TaskComment]] = None
    