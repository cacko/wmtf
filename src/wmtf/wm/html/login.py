from wmtf.wm.html.parser import Parser, ParserError


class LoginError(Exception):
    pass

class MaintenanceError(Exception):
    pass

class Login(Parser):
    def __init__(self, html: bytes, id: int = 0) -> None:
        try:
            super().__init__(html, id)
        except ParserError as pe:
            msg = str(pe)
            if "The database is currently being archived" in msg:
                raise MaintenanceError(msg)
            raise LoginError(msg)

    def parse(self):
        pass
