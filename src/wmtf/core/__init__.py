import socket
from contextlib import closing
from contextlib import contextmanager
from subprocess import Popen, DEVNULL
from os import environ
import time
import os
import logging

LOG_LEVEL = os.environ.get("WMTF_LOG_LEVEL", "FATAL")
LOGGING_LEVEL = getattr(logging, LOG_LEVEL)


def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False


@contextmanager
def process_with_port(params, host: str, port: int):
    env = dict(
        environ,
        PATH=":".join([
            f"{environ.get('HOME')}/.local/bin",
            "/usr/bin",
            "/usr/local/bin",
            environ.get('PATH', "."),
        ])
    )
    proc = Popen(params, env=env, stdout=DEVNULL)
    try:
        while not check_socket(host, port):
            time.sleep(0.1)
        yield proc
    finally:
        proc.terminate()
