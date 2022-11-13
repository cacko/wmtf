# from threading import Event, Thread
from typing import Any, Optional, Type

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Horizontal, Vertical
from textual import events
from .widgets.tasks import Tasks as WidgetTasks
from .widgets.report import Report as WidgetReport
from .widgets.app_name import AppName as WidgetAppName
from wmtf import RESOURCES_PATH



class Tui(App):
    
    CSS_PATH = (RESOURCES_PATH / "app.css").as_posix()
    
    BINDINGS = [
        ("t", "toggle_tasks", "Show Tasks"),
        ("r", "toggle_report", "Show Report"),
        ("u", "reload", "Refresh"),
        ("q", "quit", "Quit"),
    ]
   
        
    def compose(self) -> ComposeResult:
        self.title = "Work Manager"
        yield Header(show_clock=True)
        yield WidgetAppName(id="appname")
        yield WidgetTasks(id="tasks", classes="box")
        yield WidgetReport(id="report", classes="box")
        yield Footer()
        
    def on_mount(self, event: events.Mount) -> None:
        self.query_one(WidgetTasks).focus()

    def action_toggle_tasks(self) -> None:
        self.query_one(WidgetTasks).focus()

    def action_toggle_report(self) -> None:
        print("show report")
        
    def action_reload(self) -> None:
        print("reload ")