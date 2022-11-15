from wmtf.wm.client import Client
from textual.app import ComposeResult
from wmtf.tui.renderables.task import Task as TaskRenderable
from wmtf.wm.models import Task as TaskModel
from textual.keys import Keys
from textual import events
from typing import Optional
from rich.text import Text
from .types import Box, Focusable
from textual.message import Message, MessageTarget


class TaskWidget(Box):
    task: Optional[TaskModel] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def title(self):
        return "Task"

    def load(self, id: int):
        self.update("Loading...")
        self.task = Client.task(id)
        self.update(self.render())

    def render(self):
        return self.get_panel(
            TaskRenderable(self.task) if self.task else Text("Not found")
        )


class Task(Focusable):

    __wdg: Optional[TaskWidget] = None
    
    class Tab(Message):
        def __init__(self, sender: MessageTarget):
            super().__init__(sender)

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
            # case Keys.Tab:
            #     self.emit_no_wait(self.Tab(self))

    def compose(self) -> ComposeResult:
        yield self.wdg

    def load(self, task_id: int):
        self.wdg.load(task_id)

    def hide(self):
        self.add_class("hidden")

    def unhide(self):
        self.remove_class("hidden")
