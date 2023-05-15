import os
from pathlib import Path
import corelog
import logging
import sys
import signal

__name__ = "wmtf"

RESOURCES_PATH = Path(__file__).parent / "resources"

corelog.register(os.environ.get("WMTF_LOG_LEVEL", "FATAL"))

__name__ = "wmtf"


def handler_stop_signals(signum, frame):
    logging.warning("Stopping app")
    sys.exit(0)
    raise RuntimeError


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

