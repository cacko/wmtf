from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Extra, Field
from pydantic.dataclasses import dataclass
from yaml import Loader, load

from wmtf.resources import wm as wm_resources


class Commands(StrEnum):
    CLOCK = "clock"
    LOGIN = "login"
    REPORT = "report"
    REPORT_ID = "report_id"
    TASKS = "tasks"
    TASK = "task"


class Method(StrEnum):
    POST = "post"
    GET = "get"


@dataclass
class LoginData:
    userToLogin: str
    passwordToLogin: str


class ReportData(BaseModel, extra=Extra.ignore):
    META_FIELD_YEAR_reportStartDate: str
    META_FIELD_MONTH_reportStartDate: str
    META_FIELD_DAY_reportStartDate: str
    reportStartDate: str
    META_FIELD_YEAR_reportEndDate: str
    META_FIELD_MONTH_reportEndDate: str
    META_FIELD_DAY_reportEndDate: str
    reportEndDate: str
    reportSortCriteria: str
    itemId: str = Field(default="820370487")
    command: str = Field(default="PersonDetails")
    reportSortDirection: str
    reportSortLastCriteria: str
    isSortRequest: bool = Field(default=False)
    reportFilterNames0: str = Field(default="person")
    reportFilterValues0: str
    reportFilterNames1: Optional[str]
    reportFilterValues1: Optional[str]
    reportFilterNames2: Optional[str]
    reportFilterValues2: Optional[str]
    reportFilterNames3: Optional[str]
    reportFilterValues3: Optional[str]


class CommandMeta(type):
    _config: Optional[dict[str, dict]] = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return super().__call__(*args, **kwds)

    @property
    def config(cls) -> dict[str, dict]:
        if not cls._config:
            cp = wm_resources
            cls._config = load(cp.read_text(), Loader=Loader)
        assert cls._config
        return cls._config

    @property
    def clock(cls) -> "Clock":
        return Clock(**cls.config.get(Commands.CLOCK.value, {}))

    @property
    def login(cls) -> "Login":
        return Login(**cls.config.get(Commands.LOGIN.value, {}))

    @property
    def tasks(cls) -> "Tasks":
        return Tasks(**cls.config.get(Commands.TASKS.value, {}))

    @property
    def task(cls) -> "Task":
        return Task(**cls.config.get(Commands.TASK.value, {}))

    @property
    def report(cls) -> "Report":
        return Report(**cls.config.get(Commands.REPORT.value, {}))

    @property
    def report_id(cls) -> "ReportId":
        return ReportId(**cls.config.get(Commands.REPORT_ID.value, {}))


@dataclass(config=ConfigDict(extra=Extra.ignore))
class Command(metaclass=CommandMeta):
    method: Method
    url: str


@dataclass(config=ConfigDict(extra=Extra.ignore))
class Clock(Command):
    data: dict[str, str]
    query: dict[str, str]


@dataclass(config=ConfigDict(extra=Extra.ignore))
class Tasks(Command):
    query: dict[str, str]


@dataclass(config=ConfigDict(extra=Extra.ignore))
class Task(Command):
    query: dict[str, str]


@dataclass(config=ConfigDict(extra=Extra.ignore))
class Login(Command):
    data: LoginData


@dataclass(config=ConfigDict(extra=Extra.ignore))
class Report(Command):
    data: ReportData


@dataclass(config=ConfigDict(extra=Extra.ignore))
class ReportId(Command):
    pass
