
from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent


class UAMeta(type):

    _instance = None

    def __call__(self, *args, **kwds):
        if not self._instance:
            self._instance = super().__call__(*args, **kwds)
        return self._instance

    @property
    def random(cls) -> str:
        return cls().getRandomUserAgent()


class UA(object, metaclass=UAMeta):

    def __init__(self):
        software = [SoftwareName.CHROME.value]
        systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        self.rotator = UserAgent(
            software_names=software, operating_systems=systems, limit=100
        )

    def getRandomUserAgent(self) -> str:
        return self.rotator.get_random_user_agent()
