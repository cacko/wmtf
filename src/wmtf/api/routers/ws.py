from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
import logging
import asyncio
from asyncio.queues import Queue, QueueEmpty
from .models import (
    Connection,
    EmptyResult,
    ErrorResult,

    Request,
    Response,
    PackatType,
    PingMessage,
    PongMessage
)

from wmtf.wm.commands import Commands
from wmtf.wm.client import Client

N_WORKERS = 4


class WSException(Exception):
    pass


router = APIRouter()


class WSConnection(object, metaclass=Connection):
    websocket: WebSocket
    __clientId: str

    def __init__(self, websocket: WebSocket, client_id: str) -> None:
        self.websocket = websocket
        self.__clientId = client_id

    async def accept(self):
        await self.websocket.accept()
        WSConnection.connections[self.__clientId] = self

    async def send_error(self, request: Request):
        await self.send(EmptyResult(id=request.id))

    async def send(self, resp: Response):
        await self.websocket.send_json(resp.dict())


class ConnectionManager:
    async def connect(self, websocket: WebSocket, client_id: str):
        connection = WSConnection(websocket=websocket, client_id=client_id)
        await connection.accept()

    def disconnect(self, client_id):
        WSConnection.remove(client_id)

    async def process_command(
        self,
        payload: Request,
        client_id: str
    ):
        assert isinstance(payload, Request)
        connection = Connection.connections[client_id]
        assert isinstance(connection, WSConnection)
        try:
            data = payload.data
            logging.info(data)
            command = Commands(data.cmd)
            assert hasattr(Client, command.value)
            await connection.send(Response(
                id=payload.id,
                data=getattr(Client, command.value)(**data.data)
            ))
        except (AssertionError, ValueError):
            await connection.send(ErrorResult())


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
                logging.info(data)

                logging.debug(f"WORKER #{n}, {data}")
                match data.get("ztype"):
                    case PackatType.PING.value:
                        ping = PingMessage(**data)
                        assert ping.id
                        await websocket.send_json(
                            PongMessage(id=ping.id).dict()
                        )
                    case _:
                        request = Request(**data)
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
            asyncio.create_task(
                get_data_and_send(n))
            for n in range(1, N_WORKERS + 1)
        ]
    )
