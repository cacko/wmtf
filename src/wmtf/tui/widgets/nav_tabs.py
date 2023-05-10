from textual.widgets import (
    TabPane,
    TabbedContent
)

from wmtf.tui.widgets.types import Focusable
from .tasks import Tasks
from .users import Users


class NavTabsWidget(Focusable):

    def compose(self):
        with TabbedContent(initial="my_tasks"):
            with TabPane("My Tasks", id="my_tasks"):
                yield Tasks(classes="shit")
            with TabPane("Users", id="users"):
                yield Users(classes="shit")
