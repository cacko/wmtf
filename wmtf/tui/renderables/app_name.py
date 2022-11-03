from pyfiglet import Figlet
from rich.text import Text


class AppName:
    def __str__(self) -> str:
        figlet = Figlet(font="thick")
        figlet_string: str = figlet.renderText("workmanager").rstrip()
        return figlet_string

    def __rich__(self) -> Text:
        return Text.from_markup("[magenta]{}[/]".format(self))
