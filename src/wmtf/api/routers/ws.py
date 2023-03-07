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

    async def handle_command(self, request: ZSONRequest):
        try:
            logging.debug(f"handle command start {request}")
            assert request.query
            command, query = CommandExec.parse(request.query)
            logging.debug(command)
            context = Context(
                client=self.__clientId,
                query=query,
                group=self.__clientId,
                id=request.id,
                source=request.source,
            )
            assert isinstance(command, CommandExec)
            with perftime(f"Command {command.method.value}"):
                response = await run_in_threadpool(command.handler, context=context)
                await context.send_async(response)
        except AssertionError as e:
            logging.error(e)
            await self.send_error(request=request)
        except Exception as e:
            logging.exception(e)
            raise WebSocketDisconnect()

    def auth(self, token: str):
        self.__user = Auth().verify_token(token)

    def send(self, response: ZSONResponse):
        if not self.__user:
            raise WSException("user is not authenticated")
        asyncio.run(self.send_async(response))

    async def send_async(self, response: ZSONResponse):
        if not self.__user:
            raise WSException("user is not authenticated")
        attachment = None
        if response.attachment:
            assert response.attachment.contentType
            assert response.attachment.path
            attachment = await run_in_threadpool(
                WSAttachment.upload,
                contentType=response.attachment.contentType,
                url=response.attachment.path,
            )
        logging.debug(response)
        assert response.id
        resp = Response(
            ztype=ZSONType.RESPONSE,
            id=response.id,
            message=response.message,
            method=response.method,
            plain=response.plain,
            attachment=attachment,
            error=response.error,
            new_id=response.new_id,
            commands=response.commands,
            icon=response.icon,
            headline=response.headline,
            start_time=response.start_time,
            status=response.status
        )
        match response.method:
            case ZMethod.FOOTY_SUBSCRIPTION_UPDATE:
                path = f"subscriptions/{response.id.split(':')[0]}/events"
                await run_in_threadpool(
                    FirestoreClient().put,
                    path=path, data=resp.dict()
                )
            case _:
                await self.websocket.send_json(resp.dict())


class ConnectionManager:
    async def connect(self, websocket: WebSocket, client_id: str):
        connection = Connection(websocket=websocket, client_id=client_id)
        await connection.accept()

    def disconnect(self, client_id):
        WSConnection.remove(client_id)

    async def process_command(self, data, client_id):
        try:
            msg = ZSONRequest(**data)
            assert isinstance(msg, ZSONRequest)
            logging.debug(f"process command {msg}")
            assert msg.query
            connection = Connection.client(clientId=client_id)
            assert isinstance(connection, WSConnection)
            match msg.method:
                case CoreMethods.LOGIN:
                    await connection.handle_login(request=msg)
                    logging.debug("process commmand after login")
                case _:
                    await connection.handle_command(request=msg)
                    logging.debug("process commmand after handle")
        except Exception as e:
            logging.exception(e)
            raise WebSocketDisconnect()


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
