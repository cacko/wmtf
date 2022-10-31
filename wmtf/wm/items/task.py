from dataclasses import dataclass
from enum import Enum

class ClockLocation(Enum):
    HOME = "home"
    OFFICE = "office"
    


@dataclass
class Task:
    id: int
    summary: str    