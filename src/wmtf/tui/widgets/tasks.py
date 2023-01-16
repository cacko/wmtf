from wmtf.tui.renderables.task_list import TaskList
from wmtf.wm.client import Client
from wmtf.wm.models import TaskInfo, ClockLocation
from typing import Optional
from textual import events
from textual.app import ComposeResult
from textual.message import Message, MessageTarget
from textual.keys import Keys
from wmtf.tui.widgets.types import Box, Focusable
from wmtf.config import app_config


class TasksWidget(Box):

    task_list: Optional[TaskList] = None

    @property
    def max_renderables_len(self) -> int:
        height: int = self.size.height
        return height - 2

    @property
    def title(self):
        return "My Tasks"

    def on_mount(self) -> None:
        self.reload()

    def reload(self):
        tasks = Client.tasks()
        self.task_list = TaskList(
            tasks,
            max_len=self.max_renderables_len,
            selected=self.task_list.selected if self.task_list else None,
        )
        self.update(self.render())

    def render(self):
        return self.get_panel(self.task_list)

    def next(self):
        if self.task_list:
            self.task_list.next()
            self.update(self.render())

    def previous(self):
        if self.task_list:
            self.task_list.previous()
            self.update(self.render())

    def load(self):
        try:
            assert self.task_list
            selected = self.task_list.selected
            assert isinstance(selected, TaskInfo)
            assert isinstance(selected.id, int)
            assert selected.group
            return selected
        except AssertionError:
            return False


    def clock(self) -> bool:
        if not self.task_list:
            return False
        if selected := self.task_list.selected:
            return Client.clock(
                selected.clock_id, ClockLocation(app_config.wm_config.location)
            )
        return False


class Tasks(Focusable):

    __wdg: Optional[TasksWidget] = None

    class Selected(Message):
        def __init__(self, sender: MessageTarget, task: TaskInfo) -> None:
            self.task = task
            super().__init__(sender)

    @property
    def wdg(self) -> TasksWidget:
        if not self.__wdg:
            self.__wdg = TasksWidget()
        return self.__wdg

    def compose(self) -> ComposeResult:
        yield self.wdg

    def clock(self) -> bool:
        return self.wdg.clock()

    def reload(self):
        self.wdg.reload()

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
