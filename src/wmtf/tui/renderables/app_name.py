from pyfiglet import Figlet
from rich.text import Text


class AppName:
    def __str__(self) -> str:
        return Figlet().renderText(text="workmanager").rstrip()

    def __rich__(self) -> Text:
        return Text.from_markup("[magenta]{}[/]".format(self))
