from operator import methodcaller
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
import logging
from pydantic import BaseModel, Extra, Field
from typing import Optional
from pathlib import Path
from PIL import Image
import asyncio
from corestring import string_hash
import time
from datetime import datetime
from fastapi.concurrency import run_in_threadpool
from asyncio.queues import Queue, QueueEmpty
from enum import StrEnum

N_WORKERS = 4


class ZSONType(StrEnum):
    PING = "ping"
    PONG = "pong"
    REQUEST = "request"
    RESPONSE = "response"


class ZSONCommand(StrEnum):
    TASKS = "tasks"
    TASK = "task"
    REPORT = "report"
    CLOCK = "clock"
    CLOCK_OFF = "clock_off"
    USER = "user"


class UnknownClientException(Exception):
    pass


class ConnectionMeta(type):
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


class WSException(Exception):
    pass


class PingMessage(BaseModel, extra=Extra.ignore):
    ztype: ZSONType = Field(default=ZSONType.PING)
    id: Optional[str] = None
    client: Optional[str] = None


class PongMessage(BaseModel, extra=Extra.ignore):
    ztype: ZSONType = Field(default=ZSONType.PONG)
    id: str


class Response(BaseModel):
    ztype: str = Field(default=ZSONType.RESPONSE)
    id: str


class Request(BaseModel):
    ztype: str = Field(default=ZSONType.REQUEST)
    id: str


router = APIRouter()


class Connection(object, metaclass=ConnectionMeta):
    websocket: WebSocket
    __clientId: str
    __user: Optional[AuthUser] = None

    def __init__(self, websocket: WebSocket, client_id: str) -> None:
        self.websocket = websocket
        self.__clientId = client_id

    async def accept(self):
        await self.websocket.accept()
        __class__.connections[self.__clientId] = self

    async def handle_login(self, request: ZSONRequest):
        assert request.query
        await run_in_threadpool(self.auth, token=request.query)
        cmds = ZSONResponse(
            method=CoreMethods.LOGIN,
            commands=CommandExec.definitions,
            client=self.__clientId,
            id=request.id,
        )
        await self.send_async(cmds)

    async def send_error(self, request: ZSONRequest):
        empty = EmptyResult()
        await self.send_async(
            ZSONResponse(
                ztype=ZSONType.RESPONSE,
                id=request.id,
                client=self.__clientId,
                group=self.__clientId,
                error=empty.error_message,
            )
        )

    async def send(self, **args, **kwargs):
        pass
        # await self.websocket.send_json(resp.dict())


class ConnectionManager:
    async def connect(self, websocket: WebSocket, client_id: str):
        connection = Connection(websocket=websocket, client_id=client_id)
        await connection.accept()

    def disconnect(self, client_id):
        WSConnection.remove(client_id)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    logging.debug([f"{k} -> {v}" for k, v in websocket.headers.items()])
    await manager.connect(websocket, client_id)
    queue: Queue = Queue()

    async def read_from_socket(websocket: WebSocket):
        async for data in websocket.iter_json():
            queue.put_nowait(data)

    async def get_data_and_send(n: int):
        while True:
            try:
                data = queue.get_nowait()
                logging.debug(f"WORKER #{n}, {data}")
                match data.get("ztype"):
                    case ZSONType.PING.value:
                        ping = PingMessage(**data)
                        assert ping.id
                        await websocket.send_json(PongMessage(id=ping.id).dict())
                    case _:
                        await manager.process_command(data, client_id)
                queue.task_done()
            except QueueEmpty:
                await asyncio.sleep(0.2)
            except WebSocketDisconnect:
                manager.disconnect(client_id)
                break
            except Exception as e:
                logging.exception(e)

    await asyncio.gather(
        read_from_socket(websocket),
        *[
            asyncio.create_task(get_data_and_send(n)) for n in range(1, N_WORKERS + 1)
        ]
    )
