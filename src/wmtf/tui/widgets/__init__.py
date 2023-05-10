from threading import Lock
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel

TIMER_LOCK = Lock()


class Action(StrEnum):
    TASKS = "tasks"
    REPORT = "report"
    TASK = "task"


class Command(BaseModel):
    action: Action
    id: Optional[int] = None
