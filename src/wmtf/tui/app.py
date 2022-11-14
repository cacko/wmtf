from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual import events
from .widgets.tasks import Tasks as WidgetTasks
from .widgets.report import Report as WidgetReport
from .widgets.task import Task as WidgetTask
from .widgets.app_name import AppName as WidgetAppName
from wmtf import RESOURCES_PATH


class Tui(App):

    CSS_PATH = (RESOURCES_PATH / "app.css").as_posix()

    BINDINGS = [
        ("t", "toggle_views", "Toggle Views"),
        ("r", "reload", "Refresh"),
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
        self.query_one(WidgetTasks).focus()

    def action_toggle_views(self) -> None:
        self.query_one(WidgetTask).toggle_class("hidden")
        self.query_one(WidgetReport).toggle_class("hidden")

    def action_reload(self) -> None:
        print("reload")
        
    def on_tasks_selected(self, message: WidgetTasks.Selected) -> None:
        task_widget = self.query_one(WidgetTask)
        task_widget.load(message.task.id)
        task_widget.unhide()
        self.query_one(WidgetReport).hide()

