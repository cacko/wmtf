from textual.widgets import Static
from rich.panel import Panel
from rich.align import AlignMethod
from rich.console import RenderableType
from textual import events
from textual.keys import Keys
from textual.widget import Widget
from rich.box import ROUNDED, DOUBLE
from textual.reactive import reactive
from typing import Optional
from textual.message import Message, MessageTarget
from textual import events
from textual.widget import Widget


class Box(Static):

    box = reactive(ROUNDED)

    @property
    def title(self):
        raise NotImplementedError

    @property
    def title_align(self) -> AlignMethod:
        return "left"

    @property
    def padding(self) -> int:
        return 1

    def get_panel(self, content: Optional[RenderableType] = None, expand: bool = True):
        if content:
            return Panel(
                content,
                title=self.title,
                title_align=self.title_align,
                padding=self.padding,
                box=self.box,
                expand=expand,
            )
        else:
            return Panel(
                "Not found",
                title=self.title,
                title_align=self.title_align,
                padding=self.padding,
                box=self.box,
                expand=expand,
            )


class Focusable(Widget, can_focus=True):
    @property
    def wdg(self) -> Box:
        raise NotImplementedError
    
    def key_tab(self):
        self.emit_no_wait(self.Tab(self))        

    def on_focus(self, event: events.Focus) -> None:
        self.wdg.box = DOUBLE

    def on_blur(self, event: events.Blur) -> None:
        self.wdg.box = ROUNDED
