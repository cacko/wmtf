from wmtf.tui.renderables.scrollable_list import ScrollableList
from textual.widgets import Static
from wmtf.wm.client import Client
from wmtf.wm.models import TaskInfo
from typing import Optional
from textual import events
from textual.app import ComposeResult
from textual.widget import Widget
from textual.keys import Keys
from textual.message import Message, MessageTarget
class TasksWidget(Static):

    scrollable_list: Optional[ScrollableList[TaskInfo]] = None
    
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
        self.update(self.scrollable_list)

    def next(self):
        if self.scrollable_list:
            self.scrollable_list.next()
            self.update(self.scrollable_list)

    def previous(self):
        if self.scrollable_list:
            self.scrollable_list.previous()
            self.update(self.scrollable_list)
            
    def load(self):
        if self.scrollable_list:
            selected = self.scrollable_list.selected
            assert(isinstance(selected, TaskInfo))
            assert(isinstance(selected.id, int))
            return selected

class Tasks(Widget, can_focus=True):
    
    class Selected(Message):
        def __init__(self, sender: MessageTarget, task: TaskInfo) -> None:
            self.task = task
            super().__init__(sender)
    
    def compose(self) -> ComposeResult:
        self.wdg = TasksWidget()
        yield self.wdg

    def on_key(self, event: events.Key) -> None:
        match event.key:
            case Keys.Up:
                self.wdg.previous()
            case Keys.Down:
                self.wdg.next()
            case Keys.Enter:
                if selected := self.wdg.load():
                    self.emit_no_wait(self.Selected(self, selected))

    def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False
