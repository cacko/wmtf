from typing import Any, Optional
from wmtf.config import app_config, WMConfig
from wmtf.wm.commands import Command, Method
from dataclasses import asdict
from functools import reduce
from requests import Response, Session
from pathlib import Path
from wmtf.wm.html.tasks import Tasks
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
        
    def do_login(self):
        cmd = Command.login
        res = self.__call(cmd, data=self.__populate(asdict(cmd.data)))
        return res.status_code == 200
    
    def do_tasks(self):
        cmd = Command.tasks
        query = self.__populate(cmd.query)
        res = self.__call(cmd, params=query)
        pth = Path('/Users/jago/Code/wmtf') / "tasks.html"
        pth.write_bytes(res.content)
        return True
    
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
                
        
