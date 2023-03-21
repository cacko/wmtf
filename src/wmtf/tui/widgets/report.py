from wmtf.api.commands import ReportRequest
from wmtf.wm.client import Client
from wmtf.wm.models import ReportDay
from textual.app import ComposeResult
from textual.reactive import reactive
from wmtf.tui.renderables.report import Days as ReportRenderable
from wmtf.api.client import WSClient
from wmtf.tui import TUI_WS_ID
from rich.status import Status
from rich.text import Text
from wmtf.tui.widgets.types import Focusable, Box, VisibilityMixin
from typing import Optional
from datetime import datetime, timedelta
from wmtf.tui.widgets import TIMER_LOCK
from textual import log
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


class ReportWidget(Box):

    __report: Optional[list[ReportDay] | Status] = None
    __running_total = reactive("")
    __running_time: Optional[RunningTime] = None
    __timer_active: Optional[TIMER_EVENT] = None

    @property
    def title(self):
        return "Report"

    def start_timer(self, event: TIMER_EVENT):
        log(f"TIMER_ACTIVE {self.__timer_active}")
        if timer := self.__timer_active:
            match timer:
                case TIMER_EVENT.RUNNING:
                    self.running_timer.pause()
                case TIMER_EVENT.LOADING:
                    self.update_timer.pause()
        match event:
            case TIMER_EVENT.RUNNING:
                self.running_timer.resume()
                self.__timer_active = event
            case TIMER_EVENT.LOADING:
                self.update_timer.resume()
                self.__timer_active = event

    def pause_timer(self):
        if timer := self.__timer_active:
            match timer:
                case TIMER_EVENT.RUNNING:
                    self.running_timer.pause()
                case TIMER_EVENT.LOADING:
                    self.update_timer.pause()
        self.__timer_active = None

    def load(self):
        TIMER_LOCK.acquire()
        self.__report = Status("Loading", spinner="dots12")
        self.__report.start()
        self.start_timer(TIMER_EVENT.LOADING)
        WSClient.send(
            TUI_WS_ID,
            ReportRequest(),
            self.update_report
        )

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(
            interval=1 / 60,
            callback=self.timer_callback,
            pause=True)
        self.running_timer = self.set_interval(
            interval=1 / 2,
            callback=self.timer_callback,
            pause=True)
        self.load()

    def timer_callback(self, *args, **kwargs) -> None:
        if isinstance(self.__report, list) and self.__running_time:
            self.__running_total = str(self.__running_time)
            self.update(self.render())
        elif isinstance(self.__report, Status):
            self.refresh()

    def update_report(self, report: list[ReportDay]):
        if isinstance(self.__report, Status):
            self.__report.stop()
            TIMER_LOCK.release()

        self.__report = report
        self.update(self.render())
        if Client.active_task:
            today = next(filter(lambda x: x.is_today, report), None)
            if today:
                self.__running_time = RunningTime(today.total_work)
                self.start_timer(TIMER_EVENT.RUNNING)
                log("time started")

    def render(self):
        if isinstance(self.__report, Status):
            return self.get_panel(self.__report)
        elif isinstance(self.__report, list):
            return self.get_panel(ReportRenderable(
                self.__report,
                self.__running_total
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
