import sys
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
import logging
import asyncio
from asyncio.queues import Queue, QueueEmpty

from wmtf.firebase.auth import Auth

from .models import (
    Connection,
    EmptyResult,
    Payload,
    Request,
    Response,
    PackatType,
    PingMessage,
    PongMessage
)

from wmtf.wm.commands import Commands
from wmtf.wm.client import Client
from wmtf.resources.dummy import login_response, tasks_response

N_WORKERS = 4
DUMMY = True


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

    async def send(self, resp: Response | EmptyResult):
        try:
            logging.debug(resp.dict())
            await self.websocket.send_text(resp.json())
        except Exception as e:
            logging.exception(e)


class ConnectionManager:
    async def connect(self, websocket: WebSocket, client_id: str):
        connection = WSConnection(websocket=websocket, client_id=client_id)
        await connection.accept()

    def disconnect(self, client_id):
        WSConnection.remove(client_id)

    def login(self, payload: Payload):
        try:
            assert payload.data
            token = payload.data.get("token")
            assert token
            assert Auth().verify_token(token=token)
        except AssertionError as e:
            logging.exception(e)
        except Exception:
            raise WebSocketDisconnect(401, "Invalid auth")

    async def process_command(
        self,
        request: Request,
        client_id: str
    ):
        assert isinstance(request, Request)
        connection = Connection.connections[client_id]
        assert isinstance(connection, WSConnection)
        try:
            data = request.data
            logging.info(data)
            command = Commands(data.cmd)
            response = Response(
                id=request.id,
                data=Payload(cmd=command)
            )
            payload = {}
            match command:
                case Commands.LOGIN:
                    self.login(data)
                    response.ztype = PackatType.LOGIN
                    payload.update(dict(
                        # result=dict(
                        #     username=app_config.wm_config.username,
                        #     location=app_config.wm_config.location
                        # )
                        result=login_response
                    ))
                case Commands.TASKS:
                    payload.update(dict(result=tasks_response))  # type: ignore
                case _:
                    assert hasattr(Client, command.value)
                    result = getattr(Client, command.value)(**data.data)
                    logging.info(result)
                    payload.update(dict(result=result))
            response.data.data = payload
            await connection.send(response)
        except AssertionError as e:
            logging.exception(e)
            # await connection.send(ErrorResult())
        except Exception as e:
            logging.exception(e)


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
                    case PackatType.PING:
                        ping = PingMessage(**data)
                        assert ping.id
                        await websocket.send_json(
                            PongMessage(id=ping.id).dict()
                        )
                    case PackatType.PONG:
                        logging.debug(f"PONG received {data}")
                    case _:
                        request = Request(**data)
                        await manager.process_command(request, client_id)
                queue.task_done()
            except QueueEmpty:
                await asyncio.sleep(0.2)
            except WebSocketDisconnect as e:
                logging.exception(e)
                manager.disconnect(client_id)
                sys.exit(1)
                break
            except Exception as e:
                logging.exception(e)
                sys.exit(1)

    await asyncio.gather(
        read_from_socket(websocket),
        *[
            asyncio.create_task(
                get_data_and_send(n))
            for n in range(1, N_WORKERS + 1)
        ]
    )
