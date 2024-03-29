from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget
from wmtf.wm.client import Client
from textual.widgets import Static
from textual.app import ComposeResult
from wmtf.tui.theme import Theme


class ActiveTaskWidget(Static):

    task_name = reactive("")
    task_work = reactive("")
    task_location = reactive("")

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(
            interval=1 / 2,
            callback=self.update_info,
            pause=True
        )
        self.update(self.render())
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
        self.refresh()

    def render(self) -> Text:
        renderable = Text(overflow="fold")
        renderable.append(self.task_location)
        renderable.append(f" {self.task_work}", Theme.colors.secondary)
        renderable.append(f" {self.task_name}",
                          Theme.colors.secondary_darken_3)
        return renderable


class ActiveTask(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = ActiveTaskWidget()
        yield self.wdg
