from textual.widgets import Static
from wmtf.wm.client import Client
from textual.app import ComposeResult
from textual.widget import Widget
from wmtf.tui.renderables.task import Task as TaskRenderable

class TaskWidget(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        pass

    def load(self, id: int):
        self.update("Loading...")
        task = Client.task(id)
        self.update(TaskRenderable(task))

class Task(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = TaskWidget(expand=True)
        yield self.wdg
        
    def load(self, task_id: int):
        self.wdg.load(task_id)

    def hide(self):
        self.add_class("hidden")
        
    def unhide(self):
        self.remove_class("hidden")