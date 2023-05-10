from textual.widgets import (
    TabPane,
    TabbedContent
)
from textual.message import Message, MessageTarget
from wmtf.tui.widgets import Command

from wmtf.tui.widgets.types import Focusable
from .tasks import Tasks
from .users import Users


class NavTabsWidget(Focusable):

    class Load(Message):
        def __init__(
            self,
            sender: MessageTarget,
            cmd: Command
        ) -> None:
            self.cmd = cmd
            super().__init__()

    def reload(self):
        self.tasks.reload()

    def compose(self):
        self.tasks = Tasks(classes="shit")
        with TabbedContent(initial="my_tasks"):
            with TabPane("My Tasks", id="my_tasks"):
                yield self.tasks
            with TabPane("Users", id="users"):
                yield Users(classes="shit")
