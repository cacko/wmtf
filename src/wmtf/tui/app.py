from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual import events
from .widgets.tasks import Tasks as WidgetTasks
from .widgets.report import Report as WidgetReport
from .widgets.task import Task as WidgetTask
from .widgets.app_name import AppName as WidgetAppName
from wmtf import RESOURCES_PATH
from wmtf.core.events import EventListener


class Tui(App):

    CSS_PATH = (RESOURCES_PATH / "app.css").as_posix()

    BINDINGS = [
        ("t", "toggle_tasks", "Show Tasks"),
        ("r", "toggle_report", "Show Report"),
        ("u", "reload", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        self.title = "Work Manager"
        yield Header(show_clock=True)
        yield WidgetAppName(id="appname")
        yield WidgetTasks(id="tasks", classes="box")
        yield WidgetReport(id="report", classes="box")
        yield WidgetTask(id="task", classes="box hidden")
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        event_listener = EventListener()
        event_listener.start()
        self.query_one(WidgetTasks).focus()

    def action_toggle_tasks(self) -> None:
        self.query_one(WidgetTasks).focus()

    def action_toggle_report(self) -> None:
        print("show report")

    def action_reload(self) -> None:
        print("reload ")
