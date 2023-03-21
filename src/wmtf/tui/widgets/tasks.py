from wmtf.api.commands import TasksRequest
from wmtf.tui import TUI_WS_ID
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
from wmtf.api.client import WSClient
from rich.text import Text


class TasksWidget(Box):

    task_list: Optional[TaskList] = None
    loading = False

    @property
    def max_renderables_len(self) -> int:
        return 20

    @property
    def title(self):
        return "My Tasks"

    def on_mount(self) -> None:
        self.reload()

    def reload(self):
        self.loading = True
        self.update(self.render())
        WSClient.send(
            TUI_WS_ID,
            TasksRequest(),
            self.update_tasks
        )

    def update_tasks(self, tasks):
        self.task_list = TaskList(
            tasks,
            max_len=self.max_renderables_len,
            selected=self.task_list.selected if self.task_list else None,
        )
        self.loading = False
        self.update(self.render())

    def render(self):
        if self.loading:
            return self.get_panel(Text(
                "Loading")
            )
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
            super().__init__()

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
                    self.post_message(self.Selected(self, selected))
