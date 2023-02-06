from wmtf.wm.models import Task as TaskModel
from wmtf.tui.renderables.markdown import Markdown
from wmtf.wm.html.parser import markdown_links
from rich.console import RenderResult, Console, ConsoleOptions
from rich.text import Text


class Task:
    def __init__(
        self,
        wrapped: TaskModel,
    ) -> None:
        self.task = wrapped

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        title = Text(overflow="ellipsis", no_wrap=True)
        title.append(self.task.summary, 'green bold')
        title.append("\n\n")
        yield title
        yield Markdown(
            markdown_links(self.task.description),
        )

        if self.task.comments:
            parts = ["## Comments"]
            for c in self.task.comments:
                parts.append(
                    f"> **{c.author}**\n>\n> {markdown_links(c.comment)}"
                )
            yield Markdown("\n\n".join(parts))
