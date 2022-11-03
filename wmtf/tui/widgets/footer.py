from rich.align import Align
from rich.columns import Columns
from rich.padding import Padding
from textual.reactive import Reactive
from textual.widgets import Footer as BaseFooter

from wmtf.tui.renderables.active_task import ActiveTask


class Footer(BaseFooter):
    mode = Reactive("describer")

    def on_mount(self) -> None:
        self.layout_size = 1

    def render(self) -> Columns:
        mode_text = Align.right(
            Padding(
                "[bold]{}[/] mode".format(self.mode),
                pad=(0, 1, 0, 1),
                style="black on yellow",
                expand=False,
            )
        )
        return Columns([ActiveTask(), mode_text], expand=True)
