from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual import events
from textual.timer import Timer
from textual.containers import Container
from .widgets.task_list import WidgetTaskList as WidgetTaskList
from .widgets.report import Report as WidgetReport
from .widgets.task import Task as WidgetTask
from .widgets.app_name import AppName as WidgetAppName
from .widgets.app_location import AppLocation as WidgetAppLocation
from .widgets.active_task import ActiveTask as WidgetActiveTask
from .widgets.alert import Alert as WidgetAlert
from .widgets.types import Focusable
from .theme import Theme
from wmtf.wm.models import ClockLocation
from wmtf.config import app_config
from webbrowser import open_new_tab
from typing import Any
from wmtf import RESOURCES_PATH
from wmtf.version import __version__


class Tui(App):

    CSS_PATH = (RESOURCES_PATH / "app.css").as_posix()

    BINDINGS = [
        ("c", "clock", "Clock On/Off"),
        ("l", "toggle_location", "Location"),
        ("v", "toggle_views", "Views"),
        ("r", "reload", "Refresh"),
        ("t", "toggle_dark", "Theme"),
        ("q", "quit", "Quit"),
    ]

    LOCATIONS = [ClockLocation.HOME.value, ClockLocation.OFFICE.value]

    __updater: Timer

    @property
    def widget_task(self) -> WidgetTask:
        return self.query_one(WidgetTask)

    @property
    def widget_task_list(self) -> WidgetTaskList:
        return self.query_one(WidgetTaskList)

    @property
    def widget_report(self) -> WidgetReport:
        return self.query_one(WidgetReport)

    @property
    def widget_location(self) -> WidgetAppLocation:
        return self.query_one(WidgetAppLocation)

    @property
    def widget_alert(self) -> WidgetAlert:
        return self.query_one(WidgetAlert)

    def get_css_variables(self) -> dict[str, str]:
        return Theme.system.generate()

    def compose(self) -> ComposeResult:
        self._bindings.bind("tab", "switch_view", show=False, priority=True)
        self.title = f"Work Manager v{__version__}"
        # yield WidgetAlert(id="alert", classes="hidden")
        yield Header(show_clock=True)
        yield Container(
            WidgetAppName(id="app_name", classes="box"),
            Container(
                WidgetAppLocation(id="app_location", classes="box"),
                WidgetActiveTask(id="active_task", classes="box"),
                id="status_info",
                classes="box",
            ),
            id="heading",
        )
        yield Container(
            WidgetTaskList(id="tasks", classes="box"),
            WidgetReport(id="report", classes="box"),
            WidgetTask(id="task", classes="box hidden"),
            id="content",
        )
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        Focusable.next().focus()
        self.__timer = self.set_interval(
            60*5, self.on_timer,
            pause=False
        )

    def on_timer(self):
        self.widget_tasks.reload()
        self.widget_report.load()

    def action_toggle_views(self) -> None:
        self.widget_task.toggle_class("hidden")
        self.widget_report.toggle_class("hidden")

    def action_reload(self) -> None:
        self.__timer.pause()
        self.widget_task_list.reload()
        self.widget_task.hide()
        self.widget_report.unhide()
        self.widget_report.load()
        self.__timer.reset()

    def action_switch_view(self):
        nxt = Focusable.next()
        if nxt:
            nxt.focus(scroll_visible=False)

    def action_clock(self):
        if self.widget_task_list.clock():
            self.action_reload()

    def action_toggle_location(self):
        self.widget_location.location(
            self.LOCATIONS[int(not self.LOCATIONS.index(
                app_config.wm_config.location))]
        )

    def action_open_browser(self, link: str):
        open_new_tab(link)

    def on_tasks_list_selected(self, message) -> None:
        self.widget_task.load(message.task.id)
        self.widget_task.unhide()
        self.widget_report.hide()

    def on_alert_error(self, message: Any):
        self.widget_alert.message(message)
        self.widget_alert.unhide()

    def watch_dark(self, dark: bool) -> None:
        Theme.system = "dark" if dark else "light"  # type: ignore
        super().watch_dark(dark)
        self.refresh()
