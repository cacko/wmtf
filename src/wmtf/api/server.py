from queue import Queue
from wmtf.config import app_config
import uvicorn
from fastapi import FastAPI
from .routers import api, ws
from fastapi.middleware.cors import CORSMiddleware
from wmtf.core.socket import check_port


def create_rest_app():
    app = FastAPI()

    origins = [
        "*",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api.router)
    app.include_router(ws.router)
    return app


class Server(object):

    api: Queue

    def __init__(self, *args, **kwargs):
        params = dict(
            app=create_rest_app,
            host=app_config.api_config.host,
            port=app_config.api_config.port,
            factory=True
        )
        assert check_port(params["port"], params["host"]) == False
        server_config = uvicorn.Config(**params)
        self.__server = uvicorn.Server(server_config)

    def start(self):
        self.__server.run()

    def stop(self):
        self.__server.should_exit = True
