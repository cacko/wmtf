from pydantic import BaseModel, Extra, Field
from enum import StrEnum
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from wmtf.wm.models import ClockLocation, ReportDay, Task, TaskInfo


class WSType(StrEnum):
    PING = "ping"
    PONG = "pong"
    REQUEST = "request"
    RESPONSE = "response"


class WSCommand(StrEnum):
    TASKS = "tasks"
    TASK = "task"
    ACTIVE_TASK = "active_task"
    REPORT = "report"
    CLOCK = "clock"
    CLOCK_OFF = "clock_off"
    USER = "user"


class PingMessage(BaseModel, extra=Extra.ignore):
    ztype: WSType = Field(default=WSType.PING)
    id: UUID = Field(default_factory=uuid4)
    client: Optional[str] = None


class PongMessage(BaseModel, extra=Extra.ignore):
    ztype: WSType = Field(default=WSType.PONG)
    id: UUID = Field(default_factory=uuid4)


class WSResponse(BaseModel, extra=Extra.allow):
    ztype: str = Field(default=WSType.RESPONSE)
    command: WSCommand
    error: Optional[str] = None
    id: UUID


class WSRequest(BaseModel, extra=Extra.allow):
    ztype: str = Field(default=WSType.REQUEST)
    command: WSCommand
    id: UUID = Field(default_factory=uuid4)


class TasksRequest(WSRequest):
    command: WSCommand = Field(default=WSCommand.TASKS)


class TasksResponse(WSResponse):
    result: list[TaskInfo]


class TaskRequest(WSRequest):
    command: WSCommand = Field(default=WSCommand.TASK)
    task_id: int


class TaskResponse(WSResponse):
    result: Task


class ActiveTaskRequest(WSRequest):
    command: WSCommand = Field(default=WSCommand.ACTIVE_TASK)


class ActiveTaskResponse(WSResponse):
    result: Optional[TaskInfo]


class ClockOffRequest(WSRequest):
    clock_id: int


class ClockOffResponse(WSResponse):
    result: bool


class ClockRequest(WSRequest):
    clock_id: int
    location: ClockLocation


class ClockResponse(WSResponse):
    result: bool


class ReportRequest(WSRequest):
    command: WSCommand = Field(default=WSCommand.REPORT)
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class ReportResponse(WSResponse):
    result: list[ReportDay]
