from wmtf.wm.models import Task as TaskModel
from .markdown import Markdown


class Task:
    def __init__(
        self,
        wrapped: TaskModel,
    ) -> None:
        self.task = wrapped

    def __rich__(
        self,
    ) -> Markdown:
        parts = [f"# {self.task.summary}", self.task.description]
        if self.task.comments:
            parts.append("## Comments")
            for c in self.task.comments:
                parts.append(f"> **{c.author}**\n>\n> {c.comment}")
        return Markdown("\n\n".join(parts))
