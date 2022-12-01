from pyfiglet import Figlet
from rich.text import Text
from wmtf.tui.theme import Theme


class AppName:
    def __str__(self) -> str:
        return Figlet().renderText(text="workmanager").rstrip()

    def __rich__(self) -> Text:
        return Text(f"{self}", Theme.colors.warning_lighten_2)
