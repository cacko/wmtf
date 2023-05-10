

from textual.app import ComposeResult
from textual.widgets import TabPane, TabbedContent
from wmtf.tui.widgets.types import Focusable
from typing import Optional
from .spinner import SpinnerWidget
from .task import Task as WidgetTask
from .report import ReportWidget, ActiveReportDay


class Content(Focusable):
    __spinner_widget: Optional[SpinnerWidget] = None

    @property
    def wdg_loading(self) -> SpinnerWidget:
        if not self.__spinner_widget:
            self.__spinner_widget = SpinnerWidget()
        return self.__spinner_widget

    def on_report_widget_loading(self, message: ReportWidget.Loading):
        if message.res:
            self.wdg_loading.start()
            self.wdg_loading.unhide()
        else:
            self.wdg_loading.stop()
            self.wdg_loading.hide()

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="report"):
            with TabPane("Report", id="report"):
                yield self.wdg_loading
                yield ActiveReportDay()
                yield ReportWidget()
            with TabPane("Task", id="task"):
                WidgetTask(id="task"),
