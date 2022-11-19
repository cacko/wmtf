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
    merge_formatted_text,
    AnyFormattedText,
)
from pygments.token import Token

from wmtf.wm.models import ClockIcon, TaskInfo

style = style_from_pygments_cls(get_style_by_name("monokai"))  # type: ignore


def keyword(s: str) -> PT_FormattedText:
    return to_formatted_text(PygmentsTokens([(Token.Keyword, s)]))


def punctuation(s: str) -> PT_FormattedText:
    return to_formatted_text(PygmentsTokens([(Token.Punctuation, s)]))


def comment(s: str) -> PT_FormattedText:
    return to_formatted_text(PygmentsTokens([(Token.Comment, s)]))


def text(s: str) -> PT_FormattedText:
    return to_formatted_text(PygmentsTokens([(Token.Text, s)]))


@dataclass
class MenuItem:
    text: str
    obj: Optional[Any] = None
    disabled: Optional[str] = None

    @property
    def display(self) -> FormattedText:
        return self.text

    @property
    def value(self):
        return self.text


class TaskItem(MenuItem):
    obj: TaskInfo

    @property
    def display(self) -> AnyFormattedText:
        if self.obj.isActive:
            return merge_formatted_text(
                [
                    keyword(self.text),
                    punctuation(f" {self.clock_icon.value}"),
                ]
            )
        return text(self.obj.summary)

    @property
    def value(self):
        return self.obj.id

    @property
    def clock_icon(self) -> ClockIcon:
        return self.obj.clock.icon

class DisabledItem(MenuItem):
    
    @property
    def display(self):
        return comment(self.text)



MT = TypeVar("MT", MenuItem, TaskItem, DisabledItem, Separator)
