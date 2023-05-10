from wmtf.tui.renderables.task_list import TaskList
from wmtf.tui.widgets import Action
from wmtf.wm.client import Client
from wmtf.wm.models import TaskInfo, ClockLocation
from textual.app import ComposeResult
from textual.widgets import Static
from textual.message import Message, MessageTarget
from textual.widget import Widget
from wmtf.tui.widgets.types import Focusable
from wmtf.config import app_config
from typing import ClassVar, Optional
from textual.binding import Binding, BindingType


class TasksWidget(Static):

    task_list: Optional[TaskList] = None

    class Loading(Message):
        def __init__(self, sender: MessageTarget, res: bool) -> None:
            self.res = res
            super().__init__()

    def on_nav_tabs_widget_load(self, msg):
        if msg.cmd.action == Action.TASKS:
            self.reload()

    @property
    def max_renderables_len(self) -> int:
        height: int = self.size.height
        return height - 2

    def on_mount(self) -> None:
        self.reload()

    def reload(self):
        self.post_message(self.Loading(self, True))
        tasks = Client.tasks()
        self.task_list = TaskList(
            tasks,
            max_len=self.max_renderables_len,
            selected=self.task_list.selected if self.task_list else None,
        )
        # self.post_message(self.Loading(self, False))
        self.update(self.render())

    def render(self):
        try:
            assert self.task_list
            return self.task_list
        except AssertionError:
            return ""

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
            return ""

    def clock(self) -> bool:
        if not self.task_list:
            return ""
        if selected := self.task_list.selected:
            return Client.clock(
                selected.clock_id, ClockLocation(app_config.wm_config.location)
            )
        return False


class Tasks(Focusable, Widget):

    __wdg: Optional[TasksWidget] = None

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
    ]

    class Selected(Message):
        def __init__(self, sender: MessageTarget, task: TaskInfo) -> None:
            self.task = task
            super().__init__()

    def reload(self):
        self.wdg.reload()

    @property
    def wdg(self) -> TasksWidget:
        if not self.__wdg:
            self.__wdg = TasksWidget()
        return self.__wdg

    def compose(self) -> ComposeResult:
        yield self.wdg

    def clock(self) -> bool:
        # return self.wdg.clock()
        return ""

    def action_select_cursor(self) -> None:
        if selected := self.wdg.load():
            self.post_message(self.Selected(self, selected))

    def action_cursor_down(self) -> None:
        self.wdg.previous()

    def action_cursor_up(self) -> None:
        self.wdg.next()
