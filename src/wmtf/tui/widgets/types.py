from rich.console import RenderableType
from textual import events
from textual.widget import Widget
from textual.widgets import TabbedContent


class VisibilityMixin:
    def hide(self):
        self.add_class("hidden")  # type: ignore

    def unhide(self):
        self.remove_class("hidden")  # type: ignore


class Box(TabbedContent):

    def render(self) -> RenderableType:
        return super().render()


class Focusable(Widget, can_focus=True):

    __instances: list["Focusable"] = []
    __idx = -1

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        **kwads
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, **kwads)
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

    def on_focus(self, event: events.Focus) -> None:
        self.add_class("on-focus")

    def on_blur(self, event: events.Blur) -> None:
        self.remove_class("on-focus")
