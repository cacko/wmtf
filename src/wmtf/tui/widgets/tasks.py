from rich.console import ConsoleRenderable, RichCast
from wmtf.tui.renderables.task_list import TaskListItem
from wmtf.wm.client import Client
from wmtf.wm.models import TaskInfo
from typing import Optional
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem
from textual.message import Message, MessageTarget
from wmtf.tui.widgets.types import Box, Focusable


class TasksBox(Box):

    b_title = reactive("My Tasks")


class TaskItemWidget(Static):

    def __init__(self, task: TaskInfo, idx: int, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__task = task
        self.__index = idx

    def render(self) -> ConsoleRenderable | RichCast:
        return TaskListItem(self.__task, self.__index)


class TasksList(ListView):

    can_focus = True

# class TasksWidget(Static):

#     task_list: Optional[TaskList] = None

#     @property
#     def max_renderables_len(self) -> int:
#         height: int = self.size.height
#         return height - 2

#     def on_mount(self) -> None:
#         self.reload()


#     def render(self):
#         return self.task_list

#     def next(self):
#         if self.task_list:
#             self.task_list.next()
#             self.update(self.render())

#     def previous(self):
#         if self.task_list:
#             self.task_list.previous()
#             self.update(self.render())

#     def load(self):
#         try:
#             assert self.task_list
#             selected = self.task_list.selected
#             assert isinstance(selected, TaskInfo)
#             assert isinstance(selected.id, int)
#             assert selected.group
#             return selected
#         except AssertionError:
#             return False


#     def clock(self) -> bool:
#         if not self.task_list:
#             return False
#         if selected := self.task_list.selected:
#             return Client.clock(
#                 selected.clock_id, ClockLocation(app_config.wm_config.location)
#             )
#         return False


class Tasks(Focusable):

    __box: Optional[TasksBox] = None
    __wdg: Optional[TasksList] = None

    class Selected(Message):
        def __init__(self, sender: MessageTarget, task: TaskInfo) -> None:
            self.task = task
            super().__init__()

    @property
    def box(self) -> Box:
        if not self.__box:
            self.__box = TasksBox(self.wdg)
        return self.__box

    @property
    def wdg(self) -> TasksList:
        if not self.__wdg:
            self.__wdg = TasksList(*self.reload(), classes="scroll")
        return self.__wdg

    def compose(self) -> ComposeResult:
        yield self.box

    def reload(self) -> list[ListItem]:
        tasks = Client.tasks()
        return [ListItem(TaskItemWidget(t, idx)) for idx, t in enumerate(tasks)]

    # def clock(self) -> bool:
    #     return self.wdg.clock()

    # def reload(self):
    #     self.wdg.reload()

    # def on_key(self, event: events.Key) -> None:
    #     if not self.has_focus:
    #         return
    #     match event.key:
    #         case Keys.Up:
    #             self.wdg.previous()
    #         case Keys.Down:
    #             self.wdg.next()
    #         case Keys.Enter:
    #             if selected := self.wdg.load():
    #                 self.post_message(self.Selected(self, selected))
