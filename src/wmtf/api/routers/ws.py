from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
import logging
import asyncio
from asyncio.queues import Queue, QueueEmpty
import json
from wmtf.api.commands import (
    ActiveTaskRequest,
    ActiveTaskResponse,
    ClockOffRequest,
    ClockOffResponse,
    ClockRequest,
    ClockResponse,
    PingMessage,
    PongMessage,
    ReportRequest,
    ReportResponse,
    TaskRequest,
    TaskResponse,
    TasksResponse,
    WSCommand,
    WSRequest,
    WSResponse,
    WSType
)
from wmtf.wm.client import Client

N_WORKERS = 4


router = APIRouter()


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


class Connection(object, metaclass=ConnectionMeta):
    websocket: WebSocket
    __clientId: str

    def __init__(self, websocket: WebSocket, client_id: str) -> None:
        self.websocket = websocket
        self.__clientId = client_id

    async def accept(self):
        await self.websocket.accept()
        __class__.connections[self.__clientId] = self

    async def handle_login(self, request: WSRequest):
        pass
        # assert request.query
        # await run_in_threadpool(self.auth, token=request.query)
        # cmds = ZSONResponse(
        #     method=CoreMethods.LOGIN,
        #     commands=CommandExec.definitions,
        #     client=self.__clientId,
        #     id=request.id,
        # )
        # await self.send_async(cmds)

    async def send_error(self, request: WSRequest):
        pass
        # empty = EmptyResult()
        # await self.send_async(
        #     ZSONResponse(
        #         ztype=WSType.RESPONSE,
        #         id=request.id,
        #         client=self.__clientId,
        #         group=self.__clientId,
        #         error=empty.error_message,
        #     )
        # )

    async def send(self, response: WSResponse):
        json_response = response.json()
        data = json.loads(json_response)
        await self.websocket.send_json(data)

    async def handle_command(self, request: WSRequest):
        try:
            logging.debug(f"handle command start {request}")
            match request.command:
                case WSCommand.TASKS:
                    await self.send(TasksResponse(
                        command=request.command,
                        id=request.id,
                        result=Client.tasks()
                    ))
                case WSCommand.TASK:
                    request = TaskRequest.parse_obj(request)
                    await self.send(TaskResponse(
                        command=request.command,
                        id=request.id,
                        result=Client.task(task_id=request.task_id)
                    ))

                case WSCommand.ACTIVE_TASK:
                    request = ActiveTaskRequest.parse_obj(request)
                    await self.send(ActiveTaskResponse(
                        command=request.command,
                        id=request.id,
                        result=Client.active_task
                    ))

                case WSCommand.CLOCK:
                    request = ClockRequest.parse_obj(request)
                    await self.send(ClockResponse(
                        command=request.command,
                        id=request.id,
                        result=Client.clock(
                            clock_id=request.clock_id,
                            location=request.location
                        )
                    ))

                case WSCommand.CLOCK_OFF:
                    request = ClockOffRequest.parse_obj(request)
                    await self.send(ClockOffResponse(
                        command=request.command,
                        id=request.id,
                        result=Client.clock_off(
                            clock_id=request.clock_id,
                        )
                    ))

                case WSCommand.REPORT:
                    request = ReportRequest.parse_obj(request)
                    await self.send(ReportResponse(
                        command=request.command,
                        id=request.id,
                        result=Client.report(
                            start=request.start,
                            end=request.end
                        )
                    ))
        except AssertionError as e:
            logging.error(e)
            await self.send_error(request=request)
        except Exception as e:
            logging.exception(e)
            raise WebSocketDisconnect()


class ConnectionManager:
    async def connect(self, websocket: WebSocket, client_id: str):
        connection = Connection(websocket=websocket, client_id=client_id)
        await connection.accept()

    def disconnect(self, client_id):
        Connection.remove(client_id)

    async def process_command(self, data, client_id):
        try:
            msg = WSRequest(**data)
            assert isinstance(msg, WSRequest)
            logging.debug(f"process command {msg}")
            connection = Connection.client(clientId=client_id)
            assert isinstance(connection, Connection)
            match msg.command:
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
                    case WSType.PING.value:
                        ping = PingMessage(**data)
                        assert ping.id
                        await websocket.send_json(
                            PongMessage(id=ping.id).dict()
                        )
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
            asyncio.create_task(
                get_data_and_send(n)
            ) for n in range(1, N_WORKERS + 1)
        ]
    )
