from wmtf.tui.renderables.scrollable_list import ScrollableList
from textual.widgets import Static
from wmtf.wm.client import Client
from wmtf.wm.models import TaskInfo
from typing import Optional
from textual import events
from textual.keys import Keys

class Tasks(Static):
    
    scrollable_list: Optional[ScrollableList[TaskInfo]] = None
    
    @property
    def max_renderables_len(self) -> int:
        height: int = self.size.height
        return height - 2 
    
    def on_mount(self) -> None:
        tasks = Client.tasks()
        self.scrollable_list = ScrollableList(
                tasks,
                max_len=self.max_renderables_len,
                selected=self.scrollable_list.selected
                if self.scrollable_list
                else None,
            )
        self.update(self.scrollable_list)
        
    def on_key(self, event: events.Key) -> None:
        match event.key:
            case Keys.Up:
                self.previous()
            case Keys.Down:
                self.next()
        
    def next(self) -> None:
        if self.scrollable_list is None:
            return

        self.scrollable_list.next()
        # self.tui.topic = self.scrollable_list.selected

        # self.tui.enable_describer_mode()

    def previous(self) -> None:
        if self.scrollable_list is None:
            return

        self.scrollable_list.previous()
        # self.tui.topic = self.scrollable_list.selected

        # self.tui.enable_describer_mode()

    # def on_focus(self) -> None:
    #     self.has_focus = True
    #     self.tui.focusables.current = self

    def on_blur(self) -> None:
        self.has_focus = False
