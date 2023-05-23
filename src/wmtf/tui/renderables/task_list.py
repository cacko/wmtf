from typing import List, Optional
from wmtf.wm.models import TaskInfo
from rich.text import Text
from rich.console import RichCast
from wmtf.tui.theme import Theme

from .symbols import RIGHT_TRIANGLE


class TaskListItem(RichCast):

    __selected: bool = False

    def __init__(
        self,
        wrapped: TaskInfo,
        idx: int
    ) -> None:
        self.task_info = wrapped
        self.idx = idx

    def __rich__(self):
        content = Text(overflow="ellipsis", no_wrap=True)
        item = self.task_info
        string_index = str(self.idx + 1)
        string_item = (
            f"{item.clock.icon.value} {item.summary}"
            if item.isActive
            else str(item)
        )
        if self.selected == item:
            content.append(RIGHT_TRIANGLE, Theme.colors.success_lighten_1)
            content.append(" ")
            content.append(string_index, Theme.colors.success_lighten_3)
            content.append(" ")
            content.append(string_item, Theme.colors.success_lighten_1)
        else:
            content.append("  ")
            content.append(string_index, Theme.colors.accent_lighten_2)
            content.append(" ")
            content.append(string_item, Theme.colors.accent_lighten_1 if item.isActive else None)
        content.append("\n")
        return content

    @property
    def selected(self) -> bool:
        return self.__selected

    @selected.setter
    def selected(self, selected: bool) -> None:
        self.__selected = selected
