from wmtf.api.commands import TaskRequest
from wmtf.tui import TUI_WS_ID
from textual.app import ComposeResult
from wmtf.tui.renderables.task import Task as TaskRenderable
from wmtf.wm.models import Task as TaskModel
from textual.keys import Keys
from textual import events
from typing import Optional
from rich.text import Text
from wmtf.tui.widgets.types import Box, Focusable, VisibilityMixin
from wmtf.api.client import WSClient


class TaskWidget(Box):
    taskModel: Optional[TaskModel] = None
    loading = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def title(self):
        return "Task"

    def load(self, id: int):
        self.loading = True
        self.update(self.render())
        WSClient.send(
            TUI_WS_ID,
            TaskRequest(task_id=id),
            self.update_task
        )

    def update_task(self, task):
        self.taskModel = task
        self.loading = False
        self.update(self.render())

    def render(self):
        if self.loading:
            return self.get_panel(Text(
                "Loading")
            )
        return self.get_panel(
            TaskRenderable(self.taskModel) if self.taskModel else Text(
                "Not found")
        )


class Task(VisibilityMixin, Focusable):

    __wdg: Optional[TaskWidget] = None

    @property
    def wdg(self) -> TaskWidget:
        if not self.__wdg:
            self.__wdg = TaskWidget()
        return self.__wdg

    def on_key(self, event: events.Key) -> None:
        if not self.has_focus:
            return
        match event.key:
            case Keys.Up:
                self.scroll_up()
            case Keys.Down:
                self.scroll_down()

    def compose(self) -> ComposeResult:
        yield self.wdg

    def load(self, task_id: int):
        self.wdg.load(task_id)
