from pathlib import Path
from typing import Optional

from appdir import get_app_dir
from yaml import Loader, load, dump


from pydantic import BaseModel, Extra, Field

from wmtf import __name__


class WMConfig(BaseModel, extra=Extra.ignore):
    host: str = Field(default="https://workmanager.travelfusion.com")
    location: str = Field(default="office")
    username: Optional[str] = Field(default="")
    password: Optional[str] = Field(default="")


class JiraConfig(BaseModel, extra=Extra.ignore):
    host: str = Field(default="https://newsupport.travelfusion.com")
    username: Optional[str] = Field(default="")
    password: Optional[str] = Field(default="")


class app_config_meta(type):
    _instance = None

    def __call__(self, *args, **kwds):
        if not self._instance:
            self._instance = super().__call__(*args, **kwds)
        return self._instance

    def get(cls, var, *args, **kwargs):
        return cls().getvar(var, *args, **kwargs)

    def set(cls, var, value, *args, **kwargs):
        return cls().setvar(var, value, *args, **kwargs)

    @property
    def app_dir(cls):
        return Path(get_app_dir(__name__)).expanduser()

    @property
    def app_config(cls) -> Path:
        return cls.app_dir / "config.yaml"

    @property
    def cache_dir(cls):
        return cls.app_dir / "cache"

    @property
    def wm_config(cls) -> WMConfig:
        return WMConfig(**cls().getvar("wm"))

    @property
    def jira_config(cls) -> JiraConfig:
        return JiraConfig(**cls().getvar("jira"))

    @property
    def is_new(cls) -> bool:
        wm_config = cls.wm_config
        return not all([wm_config.username, wm_config.password])


class app_config(object, metaclass=app_config_meta):

    _config: Optional[dict] = None

    def __init__(self) -> None:
        if not __class__.app_config.exists():
            self.init()
        self._config = load(__class__.app_config.read_text(), Loader=Loader)

    def init(self):
        with open(__class__.app_config, "w") as fp:
            data = {"wm": WMConfig().dict(), "jira": JiraConfig().dict()}
            dump(data, fp)

    def getvar(self, var, *args, **kwargs):
        assert isinstance(self._config, dict)
        return self._config.get(var, *args, *kwargs)

    def __save(self):
        with open(__class__.app_config, "w") as fp:
            dump(self._config, fp)

    def setvar(self, var, value, *args, **kwargs):
        assert isinstance(self._config, dict)
        section, key = var.split(".")
        assert section
        assert key
        self._config[section][key] = value
        self.__save()
