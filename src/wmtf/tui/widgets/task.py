from wmtf.tui.widgets import Action
from wmtf.wm.client import Client
from textual.app import ComposeResult
from wmtf.tui.renderables.task import Task as TaskRenderable
from wmtf.wm.models import Task as TaskModel
from textual.keys import Keys
from textual import events
from textual.widgets import Static
from typing import Optional
from rich.text import Text
from wmtf.tui.widgets.types import Focusable, VisibilityMixin
from wmtf.tui.app import Tui


class TaskWidget(Static):
    taskModel: Optional[TaskModel] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_app_load(self, msg: Tui.Load):
        if msg.cmd == Action.TASKS:
            self.load()

    def load(self, id: int):
        self.update("Loading...")
        self.taskModel = Client.task(id)
        self.update(self.render())

    def render(self):
        return TaskRenderable(self.taskModel) if self.taskModel else Text(
            "Not found")


class Task(VisibilityMixin, Focusable):

    def on_key(self, event: events.Key) -> None:
        if not self.has_focus:
            return
        match event.key:
            case Keys.Up:
                self.scroll_up()
            case Keys.Down:
                self.scroll_down()

    def compose(self) -> ComposeResult:
        yield TaskWidget()
