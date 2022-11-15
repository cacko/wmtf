from wmtf.tui.renderables.scrollable_list import ScrollableList
from textual.widgets import Static
from wmtf.wm.client import Client
from wmtf.wm.models import TaskInfo
from rich.panel import Panel
from typing import Optional
from textual import events
from textual.app import ComposeResult
from textual.widget import Widget
from textual.keys import Keys
from textual.message import Message, MessageTarget
from rich.box import ROUNDED, DOUBLE
from textual.reactive import reactive


class TasksWidget(Static):

    scrollable_list: Optional[ScrollableList[TaskInfo]] = None
    box = reactive(ROUNDED)

    @property
    def max_renderables_len(self) -> int:
        height: int = self.size.height
        return height - 2

    def on_mount(self) -> None:
        tasks = Client.tasks()
        self.scrollable_list = ScrollableList(
            tasks,
            max_len=self.max_renderables_len,
            selected=self.scrollable_list.selected if self.scrollable_list else None,
        )
        self.update(self.render())

    def render(self):
        return Panel(
            self.scrollable_list,
            title="My Tasks",
            title_align="left",
            padding=1,
            box=self.box,
        )

    def next(self):
        if self.scrollable_list:
            self.scrollable_list.next()
            self.update(self.render())

    def previous(self):
        if self.scrollable_list:
            self.scrollable_list.previous()
            self.update(self.render())

    def load(self):
        if self.scrollable_list:
            selected = self.scrollable_list.selected
            assert isinstance(selected, TaskInfo)
            assert isinstance(selected.id, int)
            return selected


class Tasks(Widget, can_focus=True):
    class Selected(Message):
        def __init__(self, sender: MessageTarget, task: TaskInfo) -> None:
            self.task = task
            super().__init__(sender)

    class Tab(Message):
        def __init__(self, sender: MessageTarget):
            super().__init__(sender)

    def compose(self) -> ComposeResult:
        self.wdg = TasksWidget()
        yield self.wdg

    def on_key(self, event: events.Key) -> None:
        if not self.has_focus:
            return
        match event.key:
            case Keys.Up:
                self.wdg.previous()
            case Keys.Down:
                self.wdg.next()
            case Keys.Enter:
                if selected := self.wdg.load():
                    self.emit_no_wait(self.Selected(self, selected))
            case Keys.Tab:
                self.emit_no_wait(self.Tab(self))

    def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True
        self.wdg.box = DOUBLE

    def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False
        self.wdg.box = ROUNDED
