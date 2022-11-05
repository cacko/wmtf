from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ClockLocation(Enum):
    HOME = "home"
    OFFICE = "office"
    OFF = "off"
    


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
    