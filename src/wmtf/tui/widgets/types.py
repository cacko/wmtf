from venv import logger
from textual.containers import Container
from rich.console import RenderableType
from textual import events
from textual.widget import Widget
from textual.reactive import reactive


class VisibilityMixin:
    def hide(self):
        self.add_class("hidden")  # type: ignore

    def unhide(self):
        self.remove_class("hidden")  # type: ignore


class Box(Container):

    b_title = reactive("")
    b_padding = reactive(1)
    b_classes = reactive("box-normal")
    can_focus_children = True

    def render(self) -> RenderableType:
        self.classes = self.b_classes
        self.border_title = self.b_title
        self.styles.padding = self.b_padding
        return super().render()


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
        self.box.b_classes = "box-focused"
        logger.warn(self.children)
        self.children[0].focus()

    def on_blur(self, event: events.Blur) -> None:
        self.box.b_classes = "box-normal"
