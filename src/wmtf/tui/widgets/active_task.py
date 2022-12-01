from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget
from wmtf.wm.models import TaskInfo
from wmtf.wm.client import Client
from typing import Optional
from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from rich.text import Text
from wmtf.tui.theme import Theme


class ActiveTaskWidget(Static):

    task_name = reactive("")
    task_work = reactive("")
    task_location = reactive("")

    __task: Optional[TaskInfo] = None

    def on_mount(self) -> None:
        self.update(self.render())
        self.update_timer = self.set_interval(1 / 60, self.update_info, pause=True)
        self.update_timer.resume()

    def update_info(self):
        active_task = Client.active_task
        if active_task:
            self.task_name = active_task.summary
            self.task_work = active_task.work_display
            self.task_location = active_task.clock.icon.value
        else:
            self.task_name = ""
            self.task_work = ""

    def render(self) -> Text:
        renderable = Text(overflow="fold")
        renderable.append(self.task_location)
        renderable.append(f" {self.task_work}", Theme.colors.secondary)
        renderable.append(f" {self.task_name}", Theme.colors.secondary_darken_3)
        return renderable


class ActiveTask(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = ActiveTaskWidget()
        yield self.wdg
