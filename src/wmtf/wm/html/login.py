from wmtf.wm.html.parser import Parser, ParserError, MaintenanceError


class LoginError(Exception):
    pass


class Login(Parser):
    def __init__(self, html: bytes, id: int = 0) -> None:
        try:
            super().__init__(html, id)
        except ParserError as pe:
            raise LoginError(str(pe))

    def parse(self):
        pass
