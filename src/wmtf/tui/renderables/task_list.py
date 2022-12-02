from typing import List, Optional
from wmtf.wm.models import TaskInfo
from rich.text import Text
from rich.console import RichCast
from wmtf.tui.theme import Theme

from .symbols import RIGHT_TRIANGLE


class TaskList(RichCast):
    __pointer: int = -1

    def __init__(
        self,
        wrapped: List[TaskInfo],
        max_len: int = -1,
        pointer: int = -1,
        selected: Optional[TaskInfo] = None,
    ) -> None:
        self.list = wrapped if wrapped else []
        self.max_len = (
            len(self.list) if max_len < 0 or max_len > len(self.list) else max_len
        )
        self.start_rendering = 0
        self.end_rendering = self.max_len
        if 0 <= pointer < len(self.list):
            self.pointer = pointer

        if selected is not None:
            self.selected = selected

    def __rich__(self):
        content = Text(overflow="ellipsis", no_wrap=True)
        for index in range(self.start_rendering, self.end_rendering):
            item = self.list[index]
            string_index = str(index + 1)
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
    def selected(self) -> Optional[TaskInfo]:
        if self.pointer < 0 or self.pointer >= len(self.list):
            return None

        return self.list[self.pointer]

    @selected.setter
    def selected(self, selected: Optional[TaskInfo]) -> None:
        if selected is None:
            self.reset()
            return

        if selected in self.list:
            self.pointer = self.list.index(selected)
        else:
            self.reset()

    def __str__(self) -> str:
        return str(self.renderables())

    def renderables(self) -> List[TaskInfo]:
        return self.list[self.start_rendering : self.end_rendering]

    def reset(self) -> None:
        self.__pointer = -1
        self.start_rendering = 0
        self.end_rendering = self.max_len

    @property
    def pointer(self) -> int:
        return self.__pointer

    @pointer.setter
    def pointer(self, pointer: int) -> None:
        if pointer < 0:
            self.__pointer = len(self.list) - 1
            self.end_rendering = len(self.list)
            self.start_rendering = self.end_rendering - self.max_len
        elif pointer >= len(self.list):
            self.__pointer = 0
            self.start_rendering = 0
            self.end_rendering = self.max_len
        elif pointer < self.start_rendering:
            self.__pointer = pointer
            self.start_rendering = pointer
            self.end_rendering = pointer + self.max_len
        elif pointer >= self.end_rendering:
            self.__pointer = pointer
            self.start_rendering = pointer - self.max_len + 1
            self.end_rendering = pointer + 1
        else:
            self.__pointer = pointer

    def previous(self) -> None:
        self.pointer -= 1

    def next(self) -> None:
        self.pointer += 1
