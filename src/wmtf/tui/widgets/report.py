from ast import Load
from wmtf.wm.client import Client
from wmtf.wm.models import ReportDay
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import LoadingIndicator
from wmtf.tui.renderables.report import Days as ReportRenderable
from corethread import StoppableThread
from rich.text import Text
from wmtf.tui.widgets.types import Focusable, Box, VisibilityMixin
from typing import Optional
from datetime import datetime, timedelta
from enum import IntEnum


class TIMER_EVENT(IntEnum):
    LOADING = 1
    RUNNING = 2


class RunningTime(object):

    __last_checked: datetime

    def __init__(self, running_time: timedelta) -> None:
        self.__running_time = running_time
        self.__last_checked = datetime.now()

    def __str__(self) -> str:
        now = datetime.now()
        self.__running_time += now - self.__last_checked
        self.__last_checked = now
        return str(self.__running_time).split(".")[0]


class ReportService(StoppableThread):
    def __init__(self, callback, *args, **kwargs):
        self.__callback = callback
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        days = Client.report()
        self.__callback(days)


class ReportWidget(Box):

    __report: Optional[list[ReportDay]] = None
    __loading: bool = False

    @property
    def title(self):
        return "Report"

    def load(self):
        self.__loading = True
        t = ReportService(self.update_report)
        t.start()

    def on_mount(self) -> None:
        self.load()

    def timer_callback(self, *args, **kwargs) -> None:
        if isinstance(self.__report, list):
            self.update(self.render())

    def update_report(self, report: list[ReportDay]):
        self.__loading = False
        self.__report = report
        self.update(self.render())
        # if Client.active_task:
        #     today = next(filter(lambda x: x.is_today, report), None)
        #     if today:
        #         self.__running_time = RunningTime(today.total_work)

    def render(self):
        if self.__loading:
            return self.get_panel(Text("loading"))
        elif isinstance(self.__report, list):
            return self.get_panel(ReportRenderable(
                self.__report,
            ))
        return self.get_panel(Text("NOT FOUND"))


class Report(VisibilityMixin, Focusable):

    __wdg: Optional[ReportWidget] = None

    @property
    def wdg(self) -> ReportWidget:
        if not self.__wdg:
            self.__wdg = ReportWidget(expand=True)
        return self.__wdg

    def compose(self) -> ComposeResult:
        yield self.wdg

    def load(self):
        self.wdg.load()
