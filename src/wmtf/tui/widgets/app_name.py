from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from wmtf.tui.renderables.app_name import AppName as AppNameRenderable


class AppNameWidget(Static):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self.update(AppNameRenderable())
            

class AppName(Widget):
    def compose(self) -> ComposeResult:
        self.wdg = AppNameWidget(expand=True)
        yield self.wdg
        
