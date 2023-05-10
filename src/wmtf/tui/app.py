from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual import events
from textual.containers import Container, Horizontal, VerticalScroll
from wmtf.tui.widgets import Action, Command
from wmtf.tui.widgets.nav_tabs import NavTabsWidget
from .widgets.tasks import Tasks as WidgetTasks
from .widgets.content import Content as ContentWidget
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
from app_version import get_string_version
from wmtf.wm.client import Client

class Tui(App):

    CSS_PATH = (RESOURCES_PATH / "app.css").as_posix()

    BINDINGS = [
        ("c", "clock", "Clock On/Off"),
        ("l", "toggle_location", "Location"),
        ("v", "toggle_views", "Views"),
        ("r", "blowme", "Refresh"),
        ("t", "toggle_dark", "Theme"),
        ("q", "quit", "Quit"),
    ]

    LOCATIONS = [ClockLocation.HOME.value, ClockLocation.OFFICE.value]

    @property
    def widget_location(self) -> WidgetAppLocation:
        return self.query_one(WidgetAppLocation)

    @property
    def widget_alert(self) -> WidgetAlert:
        return self.query_one(WidgetAlert)

    @property
    def content_widget(self) -> ContentWidget:
        return self.query_one(ContentWidget)

    @property
    def navtabs_widget(self) -> NavTabsWidget:
        return self.query_one(NavTabsWidget)

    def get_css_variables(self) -> dict[str, str]:
        return Theme.system.generate()

    def compose(self) -> ComposeResult:
        self._bindings.bind("tab", "switch_view", show=False, priority=True)
        self.title = f"Work Manager v{get_string_version('wmtf')}"
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
        with Horizontal(id="content"):
            yield NavTabsWidget(classes="box scroll")
            yield ContentWidget(classes="box scroll")
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        Client.do_login()
        Focusable.next().focus()
        self.__timer = self.set_interval(
            60*5, self.on_timer,
            pause=False
        )
        self.action_blowme()

    def on_timer(self):
        # self.widget_tasks.reload()
        # self.widget_report.load()
        pass

    def action_toggle_views(self) -> None:
        pass

    def action_blowme(self) -> None:
        self.__timer.pause()
        self.content_widget.reload()
        self.navtabs_widget.reload()
        self.__timer.reset()

    def action_switch_view(self):
        nxt = Focusable.next()
        if nxt:
            nxt.focus()

    def action_clock(self):
        if self.widget_tasks.clock():
            self.action_reload()

    def action_toggle_location(self):
        self.widget_location.location(
            self.LOCATIONS[int(not self.LOCATIONS.index(
                app_config.wm_config.location))]
        )

    def action_open_browser(self, link: str):
        open_new_tab(link)

    def on_tasks_selected(self, message: WidgetTasks.Selected) -> None:
        self.post_message(ContentWidget.Load(
            self,
            Command(action=Action.TASK, id=message.task.id)
        ))

    def on_alert_error(self, message: Any):
        self.widget_alert.message(message)
        self.widget_alert.unhide()

    def watch_dark(self, dark: bool) -> None:
        Theme.system = "dark" if dark else "light"  # type: ignore
        super().watch_dark(dark)
        self.refresh()
