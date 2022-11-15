from textual.widgets import Static
from wmtf.wm.client import Client
from textual.app import ComposeResult
from textual.widget import Widget
from wmtf.tui.renderables.task import Task as TaskRenderable
from wmtf.wm.models import TaskInfo
from textual.keys import Keys
from textual.message import Message, MessageTarget
from textual import events
from textual.reactive import reactive
from typing import Optional
from rich.panel import Panel
from rich.box import ROUNDED, DOUBLE


class TaskWidget(Static):
    task: Optional[TaskInfo] = None
    box = reactive(ROUNDED)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, id: int):
        self.update("Loading...")
        self.task = Client.task(id)
        self.update(self.render())

    def render(self):
        if self.task:
            return Panel(
                TaskRenderable(self.task),
                title="Task",
                title_align="left",
                padding=1,
                box=self.box,
                expand=True,  
            )


class Task(Widget, can_focus=True):
    class Tab(Message):
        def __init__(self, sender: MessageTarget):
            super().__init__(sender)

    def on_key(self, event: events.Key) -> None:
        if not self.has_focus:
            return
        match event.key:
            case Keys.Up:
                self.scroll_up()
            case Keys.Down:
                self.scroll_down()
            case Keys.Tab:
                self.emit_no_wait(self.Tab(self))

    def compose(self) -> ComposeResult:
        self.wdg = TaskWidget(expand=True)
        yield self.wdg

    def load(self, task_id: int):
        self.wdg.load(task_id)

    def hide(self):
        self.add_class("hidden")

    def unhide(self):
        self.remove_class("hidden")

    def on_focus(self, event: events.Focus) -> None:
        self.wdg.box = DOUBLE

    def on_blur(self, event: events.Blur) -> None:
        self.wdg.box = ROUNDED
