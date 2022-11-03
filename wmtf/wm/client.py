from dataclasses import asdict
from functools import reduce
from pathlib import Path
from typing import Any, Optional

from requests import Response, Session

from wmtf.config import WMConfig, app_config
from wmtf.wm.commands import Command, Method
from wmtf.wm.html.tasks import Tasks as TasksParser
from wmtf.wm.items.task import Task


class ClientMeta(type):
    
    _instance: Optional['Client'] = None
    
    def __call__(cls, *args: Any, **kwds: Any):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance
    
    def tasks(cls):
        return cls().do_tasks()

    
class Client(object, metaclass=ClientMeta):
    
    __config: WMConfig
    __session: Optional[Session] = None
    
    def __init__(self, *args, **kwargs) -> None:
        self.__config = app_config.wm_config
        
    def __del__(self):
        if self.__session:
            self.__session.close()
        
    def do_login(self):
        cmd = Command.login
        res = self.__call(cmd, data=self.__populate(asdict(cmd.data)))
        return res.status_code == 200
    
    def do_tasks(self) -> list[Task]:
        cmd = Command.tasks
        query = self.__populate(cmd.query)
        res = self.__call(cmd, params=query)
        parser = TasksParser(res.content)
        return parser.parse()
    
    def __populate(self, data: dict[str, str], **kwds) -> dict[str, str]:
        values = {**asdict(self.__config), **kwds}
        for k, v in data.items():
            data[k] = reduce(lambda r,ck: r.replace(f'^{ck}^', values[ck]), values.keys(), v)   
        return data
    
    @property
    def session(self) -> Session:
        if not self.__session:
            self.__session = Session()
            self.do_login()
        return self.__session
    
    def __call(self, cmd: Command,  **kwds) -> Response:
        url = f'{app_config.wm_config.host}/{cmd.url}'
        match(cmd.method):
            case Method.POST:
                return self.session.post(url, **kwds)
            case Method.GET:
                return self.session.get(url, **kwds)
            case _:
                raise NotImplementedError
                
        
