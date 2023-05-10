import os
from pathlib import Path
import corelog

__name__ = "wmtf"

RESOURCES_PATH = Path(__file__).parent / "resources"

corelog.register(os.environ.get("WMTF_LOG_LEVEL", "DEBUG"))

__name__ = "wmtf"
