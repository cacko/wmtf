from queue import Queue
from wmtf.config import app_config
import uvicorn
from fastapi import FastAPI
from .routers import ws


def create_rest_app():
    app = FastAPI()

    app.include_router(ws.router)
    return app


class Server(object):

    api: Queue

    def __init__(self, *args, **kwargs):
        server_config = uvicorn.Config(
            app=create_rest_app,
            host=app_config.api_config.host,
            port=app_config.api_config.port,
            factory=True
        )
        self.__server = uvicorn.Server(server_config)

    def start(self):
        self.__server.run()

    def stop(self):
        self.__server.should_exit = True
