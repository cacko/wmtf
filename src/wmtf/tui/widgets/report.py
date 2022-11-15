from wmtf.wm.client import Client
from wmtf.wm.models import ReportDay
from textual.app import ComposeResult
from wmtf.tui.renderables.report import Report as ReportRenderable
from corethread import StoppableThread
from rich.spinner import Spinner
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

    __report: Optional[list[ReportDay]] = None

    @property
    def title(self):
        return "Report"

    def load(self):
        self.update(self.get_panel(Spinner("bouncingBall", "Loading")))
        t = ReportService(self.update_report)
        t.start()

    def on_mount(self) -> None:
        self.load()

    def update_report(self, report: list[ReportDay]):
        self.__report = report
        self.update(self.render())

    def render(self):
        return self.get_panel(
            ReportRenderable(self.__report) if self.__report else Text("Not found")
        )


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
