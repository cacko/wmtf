from wmtf.wm.client import Client
from wmtf.wm.models import ReportDay
from textual.app import ComposeResult
from textual.reactive import reactive
from wmtf.tui.renderables.report import Days as ReportRenderable
from corethread import StoppableThread
from rich.status import Status
from rich.text import Text
from wmtf.tui.widgets.types import Focusable, Box, VisibilityMixin
from typing import Optional
from datetime import datetime, timedelta
from wmtf.tui.widgets import TIMER_LOCK

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

    __report: Optional[list[ReportDay] | Status] = None
    __running_total = reactive("")
    __running_time: Optional[RunningTime] = None
    __timer_active = False

    @property
    def title(self):
        return "Report"

    def start_timer(self):
        if not self.__timer_active:
            self.update_timer.resume()
            self.__timer_active = True

    def pause_timer(self):
        self.update_timer.pause()
        self.__timer_active = False

    def load(self):
        TIMER_LOCK.acquire()
        self.__report = Status("Loading", spinner="dots12")
        self.__report.start()
        self.start_timer()
        t = ReportService(self.update_report)
        t.start()

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(1 / 60, self.on_timer, pause=True)
        self.load()
        
    def on_timer(self, *args, **kwargs) -> None:
        if isinstance(self.__report, list) and self.__running_time:
            self.__running_total = str(self.__running_time)
            self.update(self.render())
        elif isinstance(self.__report, Status):
            self.refresh()

    def update_report(self, report: list[ReportDay]):
        if isinstance(self.__report, Status):
            self.__report.stop()
            TIMER_LOCK.release()
            self.pause_timer()

        self.__report = report
        self.update(self.render())
        if Client.active_task:
            today = next(filter(lambda x: x.is_today, report), None)
            if today:
                self.__running_time = RunningTime(today.total_work)
                self.start_timer()

    def render(self):
        if isinstance(self.__report, Status):
            return self.get_panel(self.__report)
        elif isinstance(self.__report, list):
            return self.get_panel(ReportRenderable(self.__report, self.__running_total))
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
