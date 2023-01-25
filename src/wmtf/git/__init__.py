from stringcase import snakecase
from git import Diff, Repo, Head
import string
import re
from wmtf.wm.models import TaskInfo


class GitMeta(type):
    _instance: "Git" = None

    def __call__(cls, *args, **kwds):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    def createName(cls, task: TaskInfo) -> str:
        return cls().getBranchName(task)

    def create(cls, branch_name) -> Head:
        branch = cls().createBranch(branch_name)
        return branch.checkout()

    def checkout(cls, branch_name) -> Head:
        return cls().checkoutBranch(branch_name)

    def diffs(cls) -> list[Diff]:
        return cls().getDiffs()

    def patch(cls) -> str:
        return "".join([x.diff.decode() for x in cls.diffs()])

    def commit(cls, message) -> bool:
        return cls().doCommit(message)

    def push(cls):
        return cls().doPush()

    def pull(cls):
        return cls().doPull()

    @property
    def active_branch(cls) -> Head:
        return cls().getActiveBranch()


class Git(object, metaclass=GitMeta):
    repo: Repo = None

    def __init__(self) -> None:
        self.repo = Repo(".")

    def getBranchName(self, task: TaskInfo) -> str:
        tr = str.maketrans("", "", string.punctuation)
        return f"{task.id}-{snakecase((task.summary.translate(tr))):.40}".strip()

    def getActiveBranch(self) -> Head:
        return self.repo.active_branch

    def createBranch(self, name) -> Head:
        return self.repo.create_head(name)

    def checkoutBranch(self, name):
        return self.repo.git.checkout(name)

    def doPull(self):
        return self.repo.git.pull()

    def getDiffs(self) -> list[Diff]:
        return self.repo.commit().diff(None, create_patch=True)

    def doCommit(self, message):
        git = self.repo.git
        r = git.add(".")
        print(r)
        r = git.commit("-am", message)
        print(r)
        return True

    def doSvnRebase(self):
        git = self.repo.git
        git.re

    def doPush(self):
        ab = self.getActiveBranch().name
        git = self.repo.git
        r = git.push("-u", "origin", f"{ab}")
        print(r)
