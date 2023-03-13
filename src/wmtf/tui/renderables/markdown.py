from rich.markdown import Markdown as RichMarkdown, Heading
from rich.console import Console, ConsoleOptions, RenderResult, JustifyMethod
from rich.style import Style
from rich.panel import Panel
from rich.box import HORIZONTALS
from rich.text import Text
from typing import Optional, Union


class LeftHeader(Heading):
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = self.text
        text.justify = "left"
        if self.tag == "h1":
            # Draw a border around h1s
            yield Panel(
                text,
                box=HORIZONTALS,
                style="markdown.h1.border",
                padding=0
            )
        else:
            # Styled text for h2 and beyond
            if self.tag == "h2":
                yield Text("")
            yield text


class Markdown(RichMarkdown):
    def __init__(
        self,
        markup: str,
        code_theme: str = "monokai",
        justify: Optional[JustifyMethod] = None,
        style: Union[str, Style] = "none",
        hyperlinks: bool = True,
        inline_code_lexer: Optional[str] = None,
        inline_code_theme: Optional[str] = None,
    ) -> None:
        super().__init__(
            markup,
            code_theme,
            justify,
            style,
            hyperlinks,
            inline_code_lexer,
            inline_code_theme,
        )
        Markdown.elements["heading"] = LeftHeader
