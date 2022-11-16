from wmtf.wm.client import Client
from wmtf.wm.models import ReportDay
from textual.app import ComposeResult
from wmtf.tui.renderables.report import Report as ReportRenderable
from corethread import StoppableThread
from rich.status import Status
from rich.text import Text
from .types import Focusable, Box
from typing import Optional


class ReportService(StoppableThread):
    def __init__(self, callback, *args, **kwargs):
        self.__callback = callback
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        days = Client.report()
        self.__callback(days)


class ReportWidget(Box):

    __report: Optional[list[ReportDay] | Status] = None

    @property
    def title(self):
        return "Report"

    def load(self):
        self.__report = Status("Loading", spinner="bouncingBall")
        self.__report.start()
        self.update_timer.resume()
        self.update(self.render())
        t = ReportService(self.update_report)
        t.start()

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(1 / 60, self.refresh, pause=True)
        self.load()

    def update_report(self, report: list[ReportDay]):
        if isinstance(self.__report, Status):
            self.__report.stop()
            self.update_timer.pause()
        self.__report = report
        self.update(self.render())

    def render(self):
        if isinstance(self.__report, Status):
            return self.get_panel(self.__report)
        elif isinstance(self.__report, list):
            return self.get_panel(ReportRenderable(self.__report))
        else:
            return self.get_panel(Text("NOT FOUND"))


class Report(Focusable):

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

    def hide(self):
        self.add_class("hidden")

    def unhide(self):
        self.remove_class("hidden")
