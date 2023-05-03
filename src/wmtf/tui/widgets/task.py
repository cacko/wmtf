from wmtf.wm.client import Client
from textual.app import ComposeResult
from wmtf.tui.renderables.task import Task as TaskRenderable
from wmtf.wm.models import Task as TaskModel
from textual.keys import Keys
from textual import events
from textual.widgets import Static
from typing import Optional
from rich.text import Text
from wmtf.tui.widgets.types import Box, Focusable, VisibilityMixin


class TaskBox(Box):
    pass


class TaskWidget(Static):
    taskModel: Optional[TaskModel] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def title(self):
        return "Task"

    def load(self, id: int):
        self.update("Loading...")
        self.taskModel = Client.task(id)
        self.update(self.render())

    def render(self):
        return TaskRenderable(self.taskModel) if self.taskModel else Text(
            "Not found")


class Task(VisibilityMixin, Focusable):

    __wdg: Optional[TaskWidget] = None
    __box: Optional[TaskBox] = None

    @property
    def box(self) -> TaskBox:
        if not self.__box:
            self.__box = TaskBox(self.wdg)
        return self.__box

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
        yield self.box

    def load(self, task_id: int):
        self.wdg.load(task_id)
        self.box.border_title = self.wdg.title
