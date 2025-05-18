import socket
import ssl
from .base import URLHandler
from ..utils.headers import Headers

class HttpURL(URLHandler):
    _connections = {}

    def __init__(self, host: str, path: str, port: int, scheme: str):
        self.host = host
        self.path = path
        self.port = port
        self.scheme = scheme
        self.headers = Headers()
        self._set_default_headers()

    def _set_default_headers(self) -> None:
        self.headers.set("Host", self.host)
        self.headers.set("User-Agent", "My Browser")

    def request(self) -> str:
        conn_key = (self.host, self.port)
        s = self._connections.get(conn_key)

        if s is None:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
        try:
            request = "GET {} HTTP/1.1\r\n".format(self.path)
            request += str(self.headers)
            request += "\r\n"
            s.send(request.encode("utf8"))

            response = s.makefile("rb", newline="\r\n")
            statusline = response.readline().decode("utf8")
            version, status, explanation = statusline.split(" ", 2)

            response_headers = {}
            while True:
                line = response.readline().decode("utf8")
                if line == "\r\n": 
                    break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()

            if "content-length" in response_headers:
                content_length = int(response_headers["content-length"])
                content = response.read(content_length).decode("utf8")
            else:
                content = response.read().decode("utf8")

            self._connections[conn_key] = s

            return content 
        
        except Exception as e:
            if conn_key in self._connections:
                del self._connections[conn_key]
            s.close()
            raise e