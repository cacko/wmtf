import logging
from dataclasses import asdict
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path
from typing import Any, Optional

from requests import Response, Session

from wmtf.config import WMConfig, app_config
from wmtf.core.ua import UA
from wmtf.wm.commands import Command, Method
from wmtf.wm.html.report import Report as ReportParser
from wmtf.wm.html.report import ReportId as ReportIdParser
from wmtf.wm.html.login import Login as LoginParser
from wmtf.wm.html.tasks import Task as TaskParser
from wmtf.wm.html.tasks import TaskList as TaskListParser
from wmtf.wm.models import ReportDay, Task, TaskInfo


class CommandData(dict):

    __replacements: dict[str, str]

    def __init__(self, data: dict[str, Any], replacements: dict[str, str]):
        ndata = {}
        self.__replacements = replacements
        for k, v in data.items():
            ndata[self.__replace_value(k)] = self.__replace_value(v)
        super().__init__(ndata)

    def __setitem__(self, __key: Any, __value: Any) -> None:
        cval = super().__getitem__(__key)
        if not cval.startswith("$"):
            return super().__setitem__(__key, __value)
        args = cval.lstrip("$").split("|")
        value = __value
        match args.pop(0):
            case "datetime":
                value = self.__get_datetime(__value, *args)
        return super().__setitem__(__key, value)

    def __get_datetime(self, __value: datetime, *params):
        args = list(params)
        to_call = args.pop(0)
        if hasattr(__value, to_call):
            if callable(getattr(__value, to_call)):
                return getattr(__value, to_call)(*args)
            else:
                return getattr(__value, to_call)
        return __value

    def __replace_value(self, v: Any):
        if not isinstance(v, str):
            return v
        return reduce(
            lambda r, ck: r.replace(f"^{ck}^", str(self.__replacements[ck])),
            self.__replacements.keys(),
            v,
        )


class ClientMeta(type):

    _instance: Optional["Client"] = None

    def __call__(cls, *args: Any, **kwds: Any):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    def tasks(cls) -> list[TaskInfo]:
        return cls().do_tasks()

    def task(cls, task_id: int) -> Task:
        return cls().do_task(task_id)

    def clock_off(cls, clock_id: int):
        return cls().do_clock_off(clock_id)
    
    def validate_setup(cls) -> bool:
        return cls().do_login()

    def report(cls, start: Optional[datetime] = None, end: Optional[datetime] = None):
        today = datetime.today()
        if not start:
            start = (today - timedelta(days=today.weekday())).replace(
                hour=0, minute=0, second=1
            )
        if not end:
            end = today.replace(hour=23, minute=59, second=58)
        return cls().do_report(start, end)


class Client(object, metaclass=ClientMeta):

    __session: Optional[Session] = None
    __user_agent: Optional[str] = None

    @property
    def config(self) -> WMConfig:
        return app_config.wm_config

    def __del__(self):
        if self.__session:
            self.__session.close()

    def do_login(self):
        cmd = Command.login
        res = self.__call(cmd, data=self.__populate(asdict(cmd.data)))
        parser = LoginParser(res.content)
        parser.parse()
        return res.status_code == 200

    def do_clock_off(self, clock_id) -> bool:
        cmd = Command.clock
        data = self.__populate(cmd.data, clock_id=clock_id)
        query = self.__populate(cmd.query)
        res = self.__call(cmd, data=data, params=query)
        return res.status_code == 200

    def do_tasks(self) -> list[TaskInfo]:
        cmd = Command.tasks
        query = self.__populate(cmd.query)
        res = self.__call(cmd, params=query)
        content = res.content
        parser = TaskListParser(content)
        return parser.parse()

    def do_task(self, task_id: int) -> Task:
        cmd = Command.task
        query = self.__populate(cmd.query, task_id=task_id)
        res = self.__call(cmd, params=query)
        content = res.content
        parser = TaskParser(content, id=task_id)
        return parser.parse()

    def do_report(self, start: datetime, end: datetime) -> list[ReportDay]:
        cmd = Command.report_id
        res = self.__call(cmd)
        content = res.content
        parser = ReportIdParser(content)
        item_id = parser.parse()
        cmd = Command.report
        data = self.__populate(cmd.data.dict())
        data["META_FIELD_YEAR_reportStartDate"] = start
        data["META_FIELD_MONTH_reportStartDate"] = start
        data["META_FIELD_DAY_reportStartDate"] = start
        data["reportStartDate"] = start
        data["META_FIELD_YEAR_reportEndDate"] = end
        data["META_FIELD_MONTH_reportEndDate"] = end
        data["META_FIELD_DAY_reportEndDate"] = end
        data["reportEndDate"] = end
        data["itemId"] = item_id
        res = self.__call(cmd, data=data)
        content = res.content
        parser = ReportParser(content)
        return parser.parse()

    def __populate(self, data: dict[str, str], **kwds) -> CommandData:
        values = {**self.config.dict(), **kwds}
        return CommandData(data, values)

    @property
    def session(self) -> Session:
        if not self.__session:
            self.__session = Session()
            self.do_login()
        return self.__session
    
    @property
    def headers(self):
        if not self.__user_agent:
            self.__user_agent = UA.random
        return {
            "User-Agent": self.__user_agent
        }

    def __call(self, cmd: Command, **kwds) -> Response:
        url = f"{app_config.wm_config.host}/{cmd.url}"
        kw = {
            "headers": self.headers,
            **kwds
        }
        match (cmd.method):
            case Method.POST:
                return self.session.post(url, **kw)
            case Method.GET:
                return self.session.get(url, **kw)
            case _:
                raise NotImplementedError
