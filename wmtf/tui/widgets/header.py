from rich.columns import Columns
from textual.widgets import Header as BaseHeader

from wmtf.tui.renderables.app_name import AppName
from wmtf.tui.renderables.user_stat import UserStat

# from kaskade.renderables.kaskade_name import KaskadeName
# from kaskade.renderables.shortcuts_header import ShortcutsHeader
# from kaskade.widgets.tui_widget import TuiWidget


class Header(BaseHeader):
    def on_mount(self) -> None:
        self.layout_size = 3

    def render(self) -> Columns:
        user_stats = UserStat()
        app_name = AppName()
        return Columns([app_name, user_stats], padding=3)
