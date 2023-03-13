import requests
import string
from wmtf.wm.models import TaskInfo
from typing import Optional


class MessageMeta(type):

    _instance: Optional["Message"] = None

    def __call__(cls, *args, **kwds):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    def random(cls) -> str:
        return cls().getRandom()

    def branch(cls, task: TaskInfo) -> str:
        return cls().branchMessage(task)


class Message(object, metaclass=MessageMeta):
    def getRandom(self) -> str:
        req = requests.get("https://commit.cacko.net/index.txt")
        return req.content.decode().strip()

    def branchMessage(self, task: TaskInfo) -> str:
        tr = str.maketrans("", "", string.punctuation)
        return f"#{task.id} {(task.summary.translate(tr))}".strip()
