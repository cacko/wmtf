from rich.text import Text


class ActiveTask:
    def __str__(self) -> str:
        return f"alabala"

    def __rich__(self) -> Text:
        return Text.from_markup(
            "[magenta]{}[/]".format("alabala")
        )
