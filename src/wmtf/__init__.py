import logging
import os
from http.client import HTTPConnection

import structlog
from pathlib import Path

RESOURCES_PATH = Path(__file__).parent / "resources"

__name__ = "wmtf"

structlog.configure(
    processors=[
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

formatter = structlog.stdlib.ProcessorFormatter(
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.dev.ConsoleRenderer(colors=True),
    ],
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(getattr(logging, os.environ.get("WMTF_LOG_LEVEL", "INFO")))

if root_logger.getEffectiveLevel() == logging.DEBUG:
    HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
