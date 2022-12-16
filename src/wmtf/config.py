from pathlib import Path
from typing import Optional
import socket
from appdirs import user_cache_dir, user_config_dir, user_data_dir
from yaml import Loader, load, dump


from pydantic import BaseModel, Extra, Field

from wmtf import __name__


class WMConfig(BaseModel, extra=Extra.ignore):
    host: str = Field(default="https://workmanager.travelfusion.com")
    location: str = Field(default="office")
    username: str = Field(default="")
    password: str = Field(default="")


class JiraConfig(BaseModel, extra=Extra.ignore):
    host: str = Field(default="https://newsupport.travelfusion.com")
    username: str = Field(default="")
    password: str = Field(default="")


class ApiConfig(BaseModel, extra=Extra.ignore):
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=44331)
    threadpool_workers: int = Field(default=2)


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
    def config_dir(cls) -> Path:
        return Path(user_config_dir(__name__))

    @property
    def cache_dir(cls) -> Path:
        return Path(user_cache_dir(__name__))

    @property
    def data_dir(cls) -> Path:
        return Path(user_data_dir(__name__))

    @property
    def app_config(cls) -> Path:
        return cls.config_dir / "config.yaml"

    @property
    def wm_config(cls) -> WMConfig:
        return WMConfig(**cls().getvar("wm"))

    @property
    def api_config(cls) -> ApiConfig:
        return ApiConfig(**cls().getvar("api"))

    @property
    def jira_config(cls) -> JiraConfig:
        return JiraConfig(**cls().getvar("jira"))

    def is_configured(cls) -> bool:
        wm_config = cls.wm_config
        return all([wm_config.username != "", wm_config.password != ""])


class app_config(object, metaclass=app_config_meta):

    _config: Optional[dict] = None

    def __init__(self) -> None:
        if not __class__.cache_dir.exists():
            __class__.cache_dir.mkdir(parents=True, exist_ok=True)
        if not __class__.data_dir.exists():
            __class__.data_dir.mkdir(parents=True, exist_ok=True)
        if not __class__.app_config.exists():
            self.init()
        self._config = load(__class__.app_config.read_text(), Loader=Loader)
        if not self._config.get("wm", {}).get("location", ""):
            self.auto_location()

    def init(self):
        with open(__class__.app_config, "w") as fp:
            data = {
                "wm": WMConfig().dict(),
                "jira": JiraConfig().dict(),
                "api": ApiConfig().dict(),
            }
            dump(data, fp)

    def getvar(self, var, *args, **kwargs):
        assert isinstance(self._config, dict)
        return self._config.get(var, *args, *kwargs)

    def __save(self):
        with open(__class__.app_config, "w") as fp:
            dump(self._config, fp)

    def auto_location(self):
        self.setvar(
            "wm.location",
            ("office" if self.local_ip.startswith("10.1") else "home"),
        )

    @property
    def local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def setvar(self, var, value, *args, **kwargs):
        assert isinstance(self._config, dict)
        section, key = var.split(".")
        assert section
        assert key
        self._config[section][key] = value
        self.__save()
