from dataclasses import dataclass
from typing import Any, Optional
from typing import TypeVar
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name
from questionary import Separator
from questionary.prompts.common import FormattedText

from prompt_toolkit.formatted_text import (
    FormattedText as PT_FormattedText,
    PygmentsTokens,
    to_formatted_text,
)
from pygments.token import Token

from wmtf.wm.models import ClockIcon, TaskInfo

style = style_from_pygments_cls(get_style_by_name("monokai"))  # type: ignore


@dataclass
class MenuItem:
    text: str
    obj: Optional[Any] = None
    disabled: Optional[bool] = None

    @property
    def display(self) -> FormattedText:
        return self.text

    @property
    def value(self):
        return self.text

class TaskItem(MenuItem):
    obj: TaskInfo

    @property
    def display(self) -> PT_FormattedText:
        if self.obj.isActive:
            return to_formatted_text(
                PygmentsTokens(
                    [
                        (Token.Keyword, self.text),
                        (Token.Punctuation, f" {self.clock_icon.value}"),
                    ]
                )
            )
        return to_formatted_text(PygmentsTokens([(Token.Text, self.obj.summary)]))

    @property
    def value(self):
        return self.obj.id

    @property
    def clock_icon(self) -> ClockIcon:
        return self.obj.clock.icon
    

MT = TypeVar("MT", MenuItem, TaskItem, Separator)


# text = [
#     (Token.Keyword, "print"),
#     (Token.Punctuation, "("),
#     (Token.Literal.String.Double, '"'),
#     (Token.Literal.String.Double, "hello"),
#     (Token.Literal.String.Double, '"'),
#     (Token.Punctuation, ")"),
#     (Token.Text, "\n"),
# ]


