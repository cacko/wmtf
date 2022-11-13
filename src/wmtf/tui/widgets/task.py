from textual.widgets import Static
from wmtf.wm.client import Client
from textual.app import ComposeResult
from textual.widget import Widget
from wmtf.tui.renderables.task import Task as TaskRenderable
from wmtf.core.events import Action, ActionEvent, LoadTask


class TaskWidget(Static, Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        pass

    def onEvent(self, event: ActionEvent):
        match event:
            case LoadTask():
                assert isinstance(event.payload, int)
                self.load(event.payload)

    def load(self, id: int):
        task = Client.task(id)
        self.update(TaskRenderable(task))


class Task(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = TaskWidget(expand=True)
        LoadTask.register(self.wdg)
        yield self.wdg
