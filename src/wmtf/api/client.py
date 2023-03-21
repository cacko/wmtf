import asyncio
from asyncio import Queue
from typing import Callable
from corethread import StoppableThread
import websockets
from wmtf.api.commands import (
    ActiveTaskResponse,
    ClockOffResponse,
    ClockResponse,
    ReportResponse,
    TaskResponse,
    TasksResponse,
    WSCommand,
    WSResponse,
)
import json


class WSClientMeta(type):

    __instances: dict[str, 'WSClient'] = {}

    def __call__(cls, cid: str, *args, **kwds):
        if cid not in cls.__instances:
            cls.__instances[cid] = type.__call__(cls, cid, *args, **kwds)
            StoppableThread(target=cls.__instances[cid].run).start()
        return cls.__instances[cid]

    def send(cls, cid, request, callback):
        cls(cid).queue.put_nowait((request, callback))


class WSClient(object, metaclass=WSClientMeta):

    queue: Queue
    __callbacks: dict[str, Callable] = {}

    def __init__(self, cid: str):
        self.cid = cid
        self.queue = Queue()
        self.eventLoop = asyncio.new_event_loop()

    def run(self):
        self.eventLoop.create_task(self.__handler())
        self.eventLoop.run_forever()

    async def __handler(self, n_processors=3):
        uri = f"ws://localhost:44331/ws/{self.cid}"
        async with websockets.connect(uri) as ws:
            self.websocket = ws
            producers = [
                asyncio.create_task(self.__producer()),
            ]
            consumers = [
                asyncio.create_task(self.__consume(n))
                for n in range(1, n_processors + 1)
            ]
            await asyncio.gather(*producers)
            await self.queue.join()
            for c in consumers:
                c.cancel()

    async def __producer(self):
        async for received in self.websocket:
            response = WSResponse(**json.loads(received))
            callback = self.__callbacks[response.id]
            del self.__callbacks[response.id]
            match response.command:
                case WSCommand.REPORT:
                    data = ReportResponse.parse_obj(response)
                    callback(data.result)
                case WSCommand.TASKS:
                    data = TasksResponse.parse_obj(response)
                    callback(data.result)
                case WSCommand.TASK:
                    data = TaskResponse.parse_obj(response)
                    callback(data.result)
                case WSCommand.ACTIVE_TASK:
                    data = ActiveTaskResponse.parse_obj(response)
                    callback(data.result)
                case WSCommand.CLOCK:
                    data = ClockResponse.parse_obj(response)
                    callback(data.result)
                case WSCommand.CLOCK_OFF:
                    data = ClockOffResponse.parse_obj(response)
                    callback(data.result)

    async def __consume(self, name: int) -> None:
        while True:
            try:
                await self._consume_new_item(name)
            except Exception:
                continue

    async def _consume_new_item(self, name: int) -> None:
        request, callback = await self.queue.get()
        self.__callbacks[request.id] = callback
        await self.websocket.send(request.json())
        self.queue.task_done()
