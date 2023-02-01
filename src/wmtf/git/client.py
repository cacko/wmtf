# pyright: reportPrivateUsage=false

from stringcase import snakecase
from git import Diff, Repo, Head
from git.exc import (
    GitError as BaseGitError,
    InvalidGitRepositoryError
)
import string
from wmtf.wm.models import TaskInfo
from enum import StrEnum
from stringcase import sentencecase
import logging
from os import environ


class GitCommand(StrEnum):
    BRANCH_NAME = "_branch_name"
    ACTIVE_BRANCH = "_active_branch"
    CHECKOUT = "_checkout"
    DIFFS = "_diffs"
    MERGE = "_merge"
    COMMIT = "_commit"
    PUSH = "_push"
    PULL = "_pull"
    BRANCHES = "_branches"


class GitError(BaseGitError):
    
    @classmethod
    def get_cause(cls, exc: BaseGitError):
        match exc:
            case InvalidGitRepositoryError():
                return "Invalid git repository"
            case _:
                return sentencecase(exc.__class__.__name__)
    



class GitMeta(type):
    _instance: "Git" = None

    def __call__(cls, *args, **kwds):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    def branchName(cls, task: TaskInfo) -> str:
        return cls().call(GitCommand.BRANCH_NAME, task)

    def checkout(cls, branch_name) -> Head:
        return cls().call(GitCommand.CHECKOUT, branch_name)

    def diffs(cls) -> list[Diff]:
        return cls().call(GitCommand.DIFFS)

    def patch(cls) -> str:
        return "".join([x.diff.decode() for x in cls.diffs()])

    def mergeTask(cls, task: TaskInfo, *args) -> str:
        return cls().call(GitCommand.MERGE, cls.branchName(task), *args)

    def commit(cls, message) -> bool:
        return cls().call(GitCommand.COMMIT,message)

    def push(cls):
        return cls().call(GitCommand.PUSH)

    def pull(cls):
        return cls().call(GitCommand.PULL)

    def branches(cls) -> list[str]:
        return cls().call(GitCommand.BRANCHES)

    @property
    def active_branch(cls) -> Head:
        return cls().call(GitCommand.ACTIVE_BRANCH)


class Git(object, metaclass=GitMeta):
    repo: Repo = None

    def __init__(self) -> None:
        try:
            self.repo = Repo(environ.get("WMTF_GIT_REPO", "."))
        except BaseGitError as e:
            raise GitError(GitError.get_cause(e)) from e

    def call(self, cmd: GitCommand, *args, **kwds):
        try:
            method = cmd.value
            assert hasattr(self, method) and callable(getattr(self, method))
            return getattr(self, method)(*args, **kwds)
        except BaseGitError as e:
            raise GitError(GitError.get_cause(e)) from e


    def _branch_name(self, task: TaskInfo, *args) -> str:
        tr = str.maketrans("", "", string.punctuation)
        return f"{task.id}-{snakecase((task.summary.translate(tr))):.40}".strip()

    def _active_branch(self) -> Head:
        return self.repo.active_branch

    def _checkout(self, name: str):
        repo = self.repo
        head = Head(repo, f"refs/heads/{name}")
        if head.is_valid():
            return head.checkout()
        head = self.repo.create_head(name)
        return head.checkout()

    def _pull(self):
        return self.repo.git.pull()

    def _diffs(self) -> list[Diff]:
        return self.repo.commit().diff(None, create_patch=True)

    def _commit(self, message):
        git = self.repo.git
        return git.commit("-am", message)

    def _merge(self, branch: str, *args):
        git = self.repo.git
        return git.merge(branch, *args)

    def _svn_rebase(self):
        git = self.repo.git
        return git.svn("rebase")

    def _push(self):
        ab = self.getActiveBranch().name
        git = self.repo.git
        return git.push("-u", "origin", f"{ab}")

    def _branches(self):
        ls = self.repo.branches
        logging.info(ls)
