from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual import events
from textual.containers import Container
from .widgets.tasks import Tasks as WidgetTasks
from .widgets.report import Report as WidgetReport
from .widgets.task import Task as WidgetTask
from .widgets.types import Focusable

from wmtf import RESOURCES_PATH


class Tui(App):

    CSS_PATH = (RESOURCES_PATH / "app.css").as_posix()

    BINDINGS = [
        ("t", "toggle_views", "Toggle Views"),
        ("r", "reload", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    @property
    def widget_task(self) -> WidgetTask:
        return self.query_one(WidgetTask)

    @property
    def widget_tasks(self) -> WidgetTasks:
        return self.query_one(WidgetTasks)

    @property
    def widget_report(self) -> WidgetReport:
        return self.query_one(WidgetReport)

    def compose(self) -> ComposeResult:
        self._bindings.bind("tab", "switch_view", show=False, universal=True)
        self.title = "Work Manager"
        yield Header(show_clock=True)
        yield Container(
            WidgetTasks(id="tasks", classes="box"),
            WidgetReport(id="report", classes="box"),
            WidgetTask(id="task", classes="box hidden scroll"),
            id="content",
        )
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        Focusable.next().focus()

    def action_toggle_views(self) -> None:
        self.widget_task.toggle_class("hidden")
        self.widget_report.toggle_class("hidden")

    def action_reload(self) -> None:
        self.widget_task.hide()
        self.widget_report.unhide()
        self.widget_report.load()

    def action_switch_view(self):
        nxt = Focusable.next()
        if nxt:
            nxt.focus()

    def on_tasks_selected(self, message: WidgetTasks.Selected) -> None:
        self.widget_task.load(message.task.id)
        self.widget_task.unhide()
        self.widget_report.hide()
