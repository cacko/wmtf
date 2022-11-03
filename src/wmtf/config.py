from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from appdir import get_app_dir
from yaml import Loader, load

from wmtf import __name__


@dataclass
class WMConfig:
    host: str
    username: str
    password: str

@dataclass
class JiraConfig:
    host: str
    username: str
    password: str

class app_config_meta(type):
    _instance = None

    def __call__(self, *args, **kwds):
        if not self._instance:
            self._instance = super().__call__(*args, **kwds)
        return self._instance

    def get(cls, var, *args, **kwargs):
        return cls().getvar(var, *args, **kwargs)

    @property
    def app_dir(cls):
        return Path(get_app_dir(__name__)).expanduser()

    @property
    def cache_dir(cls):
        return cls.app_dir / "cache"
    
    @property
    def wm_config(cls) -> WMConfig:
        return WMConfig(**cls().getvar("wm"))

    @property
    def jira_config(cls) -> JiraConfig:
        return JiraConfig(**cls().getvar("jira"))


class app_config(object, metaclass=app_config_meta):

    _config: Optional[dict] = None

    def __init__(self) -> None:
        pth = __class__.app_dir / "config.yaml"
        self._config = load(pth.read_text(), Loader=Loader)

    def getvar(self, var, *args, **kwargs):
        if self._config:
            return self._config.get(var, *args, *kwargs)
