from textual.widgets import Static
from rich.panel import Panel
from rich.align import AlignMethod
from rich.console import RenderableType
from textual import events
from textual.widget import Widget
from rich.box import DOUBLE, SQUARE
from textual.reactive import reactive
from typing import Optional
from textual import events
from textual.widget import Widget

class VisibilityMixin:
    def hide(self):
        self.add_class("hidden")  # type: ignore

    def unhide(self):
        self.remove_class("hidden")  # type: ignore


class Box(Static):

    box = reactive(SQUARE)

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

    __instances: list["Focusable"] = []
    __idx = -1

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        __class__.__instances.append(self)

    @classmethod
    def next(cls) -> "Focusable":
        visible = list(filter(lambda x: not x.has_class("hidden"), cls.__instances))
        idx = cls.__idx + 1
        if idx >= len(visible):
            idx = 0
        cls.__idx = idx
        return visible[cls.__idx]

    @property
    def wdg(self) -> Box:
        raise NotImplementedError

    def on_focus(self, event: events.Focus) -> None:
        self.wdg.box = DOUBLE

    def on_blur(self, event: events.Blur) -> None:
        self.wdg.box = SQUARE
