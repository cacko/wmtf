from wmtf.wm.client import Client
from wmtf.wm.models import ReportDay
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static
from wmtf.tui.renderables.report import Days as ReportRenderable
from wmtf.tui.renderables.markdown import Markdown
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


class ReportBox(Box):
    b_title = reactive("Report")


class ActiveReportDay(Static):
    day_total = reactive("")
    __running_time: Optional[RunningTime] = None
    day: Optional[ReportDay] = None

    def set_day(self, day: ReportDay):
        self.day = day
        self.day_total = day.total_display
        if Client.active_task:
            self.__running_time = RunningTime(self.day.total_work)
            self.update_timer.resume()

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(
            interval=1,
            callback=self.update_info,
            pause=True
        )
        self.update(self.render())

    def update_info(self):
        self.day_total = f"{self.__running_time}"
        self.refresh()

    def render(self) -> Markdown | Text:
        try:
            parts = []
            assert self.day
            parts.append(f"# {self.day.day.strftime('%A %d %b').upper()}")
            parts.append(f"{self.day_total}")
            return Markdown(" / ".join(parts))
        except AssertionError:
            return Text("")


class ReportWidget(Static):

    __report: Optional[list[ReportDay]] = None
    __loading: bool = False
    __active_report_day: Optional[ActiveReportDay] = None

    @property
    def active_report_day(self) -> ActiveReportDay:
        if not self.__active_report_day:
            self.__active_report_day = ActiveReportDay()
        return self.__active_report_day

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
        if today := next(
                filter(lambda d: d.is_today, report), None):
            self.active_report_day.set_day(today)
        self.update(self.render())

    def render(self):
        if self.__loading:
            return Text("loading")
        elif isinstance(self.__report, list):
            return ReportRenderable(
                self.__report,
            )
        return Text("NOT FOUND")


class Report(VisibilityMixin, Focusable):
    __box: Optional[Box] = None
    __wdg_report: Optional[ReportWidget] = None

    @property
    def box(self) -> Box:
        if not self.__box:
            self.__box = ReportBox(
                self.wdg_time,
                self.wdg_report
            )
        return self.__box

    @property
    def wdg_report(self) -> ReportWidget:
        if not self.__wdg_report:
            self.__wdg_report = ReportWidget(expand=True)
        return self.__wdg_report

    @property
    def wdg_time(self) -> ActiveReportDay:
        return self.wdg_report.active_report_day

    def compose(self) -> ComposeResult:
        yield self.box

    def load(self):
        self.wdg_report.load()
