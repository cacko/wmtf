from queue import Queue
from typing import Optional
from wmtf.config import app_config
from butilka.server import BlockingServer as ButilkaServer
from butilka.server import request
from wmtf.wm.client import Client
from bottle import abort


class ServerMeta(type):

    _instance: Optional["Server"] = None

    def __call__(cls, *args, **kwds):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    @property
    def app(cls):
        return cls().app

    def user(cls):
        return cls().do_user()

    def report(cls):
        return cls().do_report()

    def tasks(cls):
        return cls().do_tasks()

    def task(cls, id):
        return cls().do_task(id)

    def clock(cls, clock_id: int, location: str):
        return cls().do_clock(clock_id, location)


class Server(ButilkaServer, metaclass=ServerMeta):

    api: Queue

    def __init__(self, *args, **kwargs):
        conf = app_config.api_config
        super().__init__(**conf.dict())

    def stop(self):
        return self.terminate()

    def do_report(self):
        days = Client.report()
        return [d.dict() for d in days]

    def do_tasks(self):
        tasks = Client.tasks()
        return [t.dict() for t in tasks]

    def do_task(self, id):
        try:
            task = Client.task(id)
            return task.dict()
        except Exception:
            abort(404, f"Task {id} not found")

    def do_clock(self, clock_id: int, location: str):
        pass

    def do_user(self):
        pass


app = Server.app


@app.route("/user")
def user():
    return Server.user()


@app.route("/report")
def report():
    return Server.report()


@app.route("/tasks")
def tasks():
    return Server.tasks()


@app.route("/task/<id:int>")
def task(id: int):
    return Server.task(id)


@app.route("/clock", method="POST")
def clock():
    data = request.json
    raise NotImplementedError
