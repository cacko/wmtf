from prompt_toolkit.formatted_text import (FormattedText, PygmentsTokens,
                                           to_formatted_text)
from pygments.token import Token

from wmtf.ui.menu import MenuItem
from wmtf.wm.items.task import Task

# text = [
#     (Token.Keyword, "print"),
#     (Token.Punctuation, "("),
#     (Token.Literal.String.Double, '"'),
#     (Token.Literal.String.Double, "hello"),
#     (Token.Literal.String.Double, '"'),
#     (Token.Punctuation, ")"),
#     (Token.Text, "\n"),
# ]


class TaskItem(MenuItem):
    obj: Task

    @property
    def display(self) -> FormattedText:
        if self.obj.isActive:
            return to_formatted_text(PygmentsTokens([(Token.Keyword, self.text)]))
        return to_formatted_text(PygmentsTokens([(Token.Text, self.obj.summary)]))

    @property
    def value(self):
        return self.obj.id
