
from enum import StrEnum
from pydantic import BaseModel, Extra, Field
from typing import Any, Optional
import requests
from emoji import emojize
from random import choice
from wmtf.wm.commands import Commands


def error_message():
    try:
        return requests.get(
            "https://commit.cacko.net/index.txt"
        ).text.strip()
    except Exception:
        return choice(NOT_FOUND)


class PackatType(StrEnum):
    PING = "ping"
    PONG = "pong"
    REQUEST = "request"
    RESPONSE = "response"


NOT_FOUND = [
    "Няма нищо брат",
    "Отиде коня у реката",
    "...and the horse went into the river",
    "Go fish!",
    "Nod fand!",
]

NOT_FOUND_ICONS = [
    ":axe:",
    ":thinking_face:",
    ":open_hands:",
    ":horse_face: :bucket:",
    ":man_walking: :left_arrow:",
]


class UnknownClientException(Exception):
    pass


class Connection(type):
    connections: dict[str, 'Connection'] = {}

    def client(cls, clientId: str) -> "Connection":
        if clientId not in cls.connections:
            raise UnknownClientException
        return cls.connections[clientId]

    def remove(cls, clientId: str):
        try:
            assert clientId in cls.connections
            del cls.connections[clientId]
        except AssertionError:
            pass


class PingMessage(BaseModel, extra=Extra.ignore):
    ztype: PackatType = Field(default=PackatType.PING)
    id: Optional[str] = None
    client: Optional[str] = None


class PongMessage(BaseModel, extra=Extra.ignore):
    ztype: PackatType = Field(default=PackatType.PONG)
    id: str


class Payload(BaseModel):
    cmd: Commands
    data: Optional[dict[str, Any]] = Field(default={})


class Response(BaseModel):
    ztype: str = Field(default=PackatType.RESPONSE)
    id: str
    data: Payload
    error: Optional[str] = None


class Request(BaseModel):
    ztype: str = Field(default=PackatType.REQUEST)
    id: str
    data: Payload


class EmptyResult(Response):
    
    def __init__(self, **data):
        super().__init__(**data)
        emo = emojize(choice(NOT_FOUND_ICONS))
        self.error = f"{emo} {error_message()}"


class ErrorResult(EmptyResult):
    
    def __init__(self, **data):
        super().__init__(**data)
        emo = emojize(choice(NOT_FOUND_ICONS))
        if not self.error:
            self.error = f"{emo} {error_message()}"
