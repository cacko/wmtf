import logging
from threading import Event
from typing import Any, Optional
from corethread import StoppableThread


class Action(object):

    def onEvent(self, event: 'ActionEvent'):
        raise NotImplementedError


class ActionEventMeta(type):
    _collectors = {}
    __events = {}

    def __call__(cls, *args, **kwds):
        k = cls.__name__
        if k not in cls.__events:
            cls.__events[k] = type.__call__(cls, *args, **kwds)
        return cls.__events[k]

    def register(cls, item):
        k = cls().__class__.__name__
        if k not in cls._collectors:
            cls._collectors[k] = []
        cls._collectors[k].append(item)

    @property
    def events(cls) -> list['ActionEvent']:
        return list(cls.__events.values())


class ActionEvent(Event, metaclass=ActionEventMeta):
    
    payload: Optional[Any] = None

    @property
    def collectors(self) -> list[Action]:
        return __class__._collectors.get(self.__class__.__name__, [])
    
    def set(self, payload: Optional[Any]) -> None:
        self.payload = payload
        return super().set()
    
    def clear(self) -> None:
        self.payload = None
        return super().clear()


class LoadTask(ActionEvent):
    pass


class TaskLoaded(ActionEvent):
    pass


class EventListener(StoppableThread):

    __events: list[ActionEvent] = []

    def __init__(self, *args, **kwargs):
        self.__events = ActionEvent.events
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        while not self.stopped():
            for ev in self.__events:
                res = ev.wait(0.1)
                if not res:
                    continue
                logging.debug(f"{ev} {res}")
                for collector in ev.collectors:
                    collector.onEvent(ev)
                ev.clear()
