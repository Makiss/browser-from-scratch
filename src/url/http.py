import socket
import ssl
from .base import URLHandler
from ..utils.headers import Headers

class HttpURL(URLHandler):
    def __init__(self, host: str, path: str, port: int, scheme: str):
        self.host = host
        self.path = path
        self.port = port
        self.scheme = scheme
        self.headers = Headers()
        self._set_default_headers()

    def _set_default_headers(self) -> None:
        self.headers.set("Host", self.host)
        self.headers.set("Connection", "close")
        self.headers.set("User-Agent", "My Browser")

    def request(self) -> str:
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} HTTP/1.1\r\n".format(self.path)
        request += str(self.headers)
        request += "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read()
        s.close()

        return content 