from wmtf.core import LOG_LEVEL
from pathlib import Path
import corelog

__name__ = "wmtf"

RESOURCES_PATH = Path(__file__).parent / "resources"

corelog.register(LOG_LEVEL)

__name__ = "wmtf"
