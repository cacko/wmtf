from rich.table import Table
from wmtf.config import app_config
from datetime import datetime
from tzlocal import get_localzone


class UserStat:
    # def __init__(self) -> None:
    #     self.cluster = cluster

    def __str__(self) -> str:
        return str(app_config.wm_config.username)

    def __rich__(self) -> Table:
        table = Table(box=None, expand=False)
        table.add_column(style="bold blue")
        table.add_column()
        table.add_row("user:", app_config.wm_config.username)
        table.add_row("time:", datetime.now(tz=get_localzone()).strftime("%c"))
        return table
