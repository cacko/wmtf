from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Extra, Field
from pydantic.dataclasses import dataclass
from yaml import Loader, load


class Commands(Enum):
    CLOCK = "clock"
    LOGIN = "login"
    REPORT = "report"
    TASKS = "tasks"


class Method(Enum):
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
    itemId: int = Field(default=820370487)
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
            cp = Path(__file__).parent.parent / "yaml" / "wm.yaml"
            cls._config = load(cp.read_text(), Loader=Loader)
        return cls._config

    @property
    def clock(cls) -> "Clock":
        return Clock(**cls.config.get(Commands.CLOCK.value))  # type: ignore

    @property
    def login(cls) -> "Login":
        return Login(**cls.config.get(Commands.LOGIN.value))  # type: ignore

    @property
    def tasks(cls) -> "Tasks":
        return Tasks(**cls.config.get(Commands.TASKS.value))  # type: ignore

    @property
    def report(cls) -> "Report":
        return Report(**cls.config.get(Commands.REPORT.value))  # type: ignore


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
class Login(Command):
    data: LoginData

@dataclass(config=ConfigDict(extra=Extra.ignore))
class Report(Command):
    data: ReportData
