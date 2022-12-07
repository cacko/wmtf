from wmtf.wm.models import Task as TaskModel
from .markdown import Markdown
from wmtf.tui.theme import Theme
from wmtf.wm.html.parser import textual_links
from rich.console import RenderResult, Console, ConsoleOptions
from textual.widgets import Static
from rich.text import Text
from random import randint
from emoji import emojize
from functools import reduce


class Task:

    __authors: dict[str, str] = {}
    __colors: list[str] = [
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "bright_black",
        "bright_red",
        "bright_green",
        "bright_yellow",
        "bright_blue",
        "bright_magenta",
        "bright_cyan",
        "navy_blue",
        "dark_blue",
        "blue3",
        "blue1",
        "dark_green",
        "dark_cyan",
        "light_sea_green",
        "dark_turquoise",
        "medium_spring_green",
        "dark_red",
        "blue_violet",
        "steel_blue",
        "cornflower_blue",
        "cadet_blue",
        "medium_turquoise",
        "dark_magenta",
        "dark_violet",
        "purple",
        "light_slate_grey",
        "light_slate_gray",
        "medium_purple",
        "light_slate_blue",
        "dark_sea_green",
        "medium_violet_red",
        "dark_goldenrod",
        "rosy_brown",
        "light_steel_blue",
        "green_yellow",
        "orchid",
        "violet",
        "tan",
        "hot_pink",
    ]

    def __init__(
        self,
        wrapped: TaskModel,
    ) -> None:
        self.task = wrapped

    def __author_colors(self, author: str):
        if author not in self.__authors:
            rand_idx = randint(0, len(self.__colors) - 1)
            rand_color = self.__colors.pop(rand_idx)
            self.__authors[author] = rand_color
        return self.__authors[author]

    @property
    def content(self):

        return reduce(
            lambda r, x: [*r, x, " "],
            map(
                lambda v: (emojize(v[0]), v[1]),
                [
                    (
                        f":open_file_folder:{self.task.group}",
                        Theme.colors.warning_lighten_2,
                    ),
                    (
                        f":alarm_clock:{self.task.estimateDisplay} ({self.task.estimate_used:.0f}%)",
                        self.task.estimate_color,
                    ),
                    (f":money_bag:{self.task.value}", Theme.colors.accent_lighten_2),
                    (
                        f":hourglass_done:{self.task.age}",
                        Theme.colors.success_lighten_2,
                    ),
                    (
                        f":chart_increasing:{self.task.priority}",
                        Theme.colors.error_lighten_2,
                    ),
                ],
            ),
            [],
        )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        title = Text(overflow="fold")
        title.append(
            self.task.summary.upper(), f"{Theme.colors.success_lighten_2} bold"
        )
        yield title
        yield Text(overflow="ellipsis").assemble(
            *self.content,
            end="\n\n",
        )
        yield Static(
            textual_links(self.task.description, "open_browser"),
            expand=True,
            classes="description",
        ).renderable

        if self.task.comments and len(self.task.comments) > 0:
            yield Text("\n")
            yield Markdown("\n\n---\n\n")
            for c in self.task.comments:
                heading = Text(
                    f"\n\n{c.author}",
                    f"{self.__author_colors(c.author)} bold",
                )
                heading.append(f" ({c.timestamp_display})", "dim")
                yield heading
                yield Static(
                    textual_links(c.comment, "open_browser"),
                    expand=True,
                    classes="comment",
                ).renderable
