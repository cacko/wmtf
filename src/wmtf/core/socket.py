import socket


def check_port(port: int, host: str = "127.0.0.1") -> bool:

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        assert result
        return False
    except AssertionError:
        return True
    finally:
        sock.close()
