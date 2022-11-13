from wmtf.wm.client import Client
from typing import Optional

class ReportMeta(type):
    
    __instance: Optional['Report'] = None
    
    def __call__(cls, *args, **kwds):
        if not cls.__instance:
            cls.__instance = type.__call__(cls, *args, **kwds)
        return cls.__instance
    
class Report(object, metaclass=ReportMeta):
    pass