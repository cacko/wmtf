from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional


class ClockLocation(Enum):
    HOME = "home"
    OFFICE = "office"
    OFF = "off"
    
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


@dataclass
class TaskInfo:
    id: int
    summary: str
    clock_id: int
    clock: ClockLocation

    @property
    def isActive(self):
        return self.clock in [ClockLocation.HOME, ClockLocation.OFFICE]

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
    