from dataclasses import dataclass
from enum import Enum

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
class Task:
    id: int