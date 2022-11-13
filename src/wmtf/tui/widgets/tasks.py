from wmtf.tui.renderables.scrollable_list import ScrollableList
from textual.widgets import Static
from wmtf.wm.client import Client
from wmtf.wm.models import TaskInfo
from typing import Optional
from textual import events
from textual.app import ComposeResult
from textual.widget import Widget
from textual.keys import Keys


class TaskWidget(Static):

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


class Tasks(Widget, can_focus=True):
    def compose(self) -> ComposeResult:
        self.wdg = TaskWidget()
        yield self.wdg

    def on_key(self, event: events.Key) -> None:
        match event.key:
            case Keys.Up:
                self.wdg.previous()
            case Keys.Down:
                self.wdg.next()
            case Keys.Enter:
                pass

    def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False
