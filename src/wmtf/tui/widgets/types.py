from textual.widgets import Static
from textual.containers import Container
from rich.panel import Panel
from rich.align import AlignMethod
from rich.console import RenderableType
from textual import events
from textual.widget import Widget
from rich.box import DOUBLE, SQUARE
from textual.reactive import reactive
from typing import Optional


class VisibilityMixin:
    def hide(self):
        self.add_class("hidden")  # type: ignore

    def unhide(self):
        self.remove_class("hidden")  # type: ignore


class Box(Container):
    
    @property
    def padding(self) -> int:
        return 1

    # def get_box(
    #     self,
    #     content: Optional[Widget] = None,
    #     expand: bool = True
    # ):
    #     if content:
    #         box = Container(
    #             content,
    #             classes=self.border,
    #         )
    #         box.border_title = self.title
    #         return box
    #     else:
    #         box = Container(
    #             Static("Not found"),
    #             classes=self.border,
    #         )
    #         box.border_title = self.title
    #         return box


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
        Focusable.__instances.append(self)

    @classmethod
    def next(cls) -> "Focusable":
        visible = list(
            filter(lambda x: not x.has_class("hidden"), cls.__instances))
        idx = cls.__idx + 1
        if idx >= len(visible):
            idx = 0
        cls.__idx = idx
        return visible[cls.__idx]

    @property
    def box(self) -> Box:
        raise NotImplementedError

    def on_focus(self, event: events.Focus) -> None:
        self.box.classes = "border-double"

    def on_blur(self, event: events.Blur) -> None:
        self.box.classes = "border-round"
