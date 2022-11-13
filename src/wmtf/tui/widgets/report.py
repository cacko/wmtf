


from textual.widgets import Static
from wmtf.wm.client import Client
from textual.app import ComposeResult
from textual.widget import Widget
from wmtf.tui.renderables.report import Report as ReportRenderable
from corethread import StoppableThread
from rich.text import Text

class ReportService(StoppableThread):
    
    def __init__(self, callback, *args, **kwargs):
        self.__callback = callback
        super().__init__(*args, **kwargs)
    
    def run(self) -> None:
        days = Client.report()
        self.__callback(ReportRenderable(days))


class ReportWidget(Static):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self.update(Text("Loading"))
        t = ReportService(self.update)
        t.start()
            

class Report(Widget, can_focus=True):
    def compose(self) -> ComposeResult:
        self.wdg = ReportWidget(expand=True)
        yield self.wdg
        
