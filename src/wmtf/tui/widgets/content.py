

from textual.app import ComposeResult
from textual.widgets import TabPane, TabbedContent
from wmtf.tui.widgets.types import Focusable
from typing import Optional
from .spinner import SpinnerWidget
from .task import Task as WidgetTask
from .report import ReportWidget, ActiveReportDay
from textual.containers import VerticalScroll
import asyncio


class Content(Focusable):
    __spinner_widget: Optional[SpinnerWidget] = None

    @property
    def wdg_loading(self) -> SpinnerWidget:
        if not self.__spinner_widget:
            self.__spinner_widget = SpinnerWidget()
        return self.__spinner_widget

    async def on_report_widget_loading(self, message: ReportWidget.Loading):
        if message.res:
            asyncio.create_task(self.wdg_loading.start()
                     asyncio.create_task       self.wdg_loading.unhide())

        else:
            asyncio.create_task(self.wdg_loading.stop())
            asyncio.create_task(self.wdg_loading.hide())

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="report", classes="scroll"):
            with TabPane("Report", id="report"):
                yield VerticalScroll(
                    self.wdg_loading,
                    ActiveReportDay(),
                    ReportWidget(classes="scroll")
                )

            with TabPane("Task", id="task"):
                yield WidgetTask(classes="shit scroll")
