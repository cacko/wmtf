from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

from wmtf.wm.client import Client


class ActiveTask(Widget):

    task: Reactive[str] = Reactive("")
    
    def on_mount(self) -> None:
        tasks = Client.tasks()
        active_task = next(filter(lambda x: x.isActive, tasks), None)
        if active_task:
            self.task = active_task.summary
        else:
            self.task = "None"
        
    def render(self) -> Text:
        return Text.from_markup("[magenta]{}[/]".format(self.task))
