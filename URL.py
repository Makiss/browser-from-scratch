import socket
import ssl
from Headers import Headers

class URL:
    def __init__(self, url: str):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        self.headers = Headers()
        self._set_default_headers()

    def request(self) -> str:
        if self.scheme == "file":
            return self._request_file()
        else:
            return self._request_page()
    
    def _set_default_headers(self) -> None:
        self.headers.set("Host", self.host)
        self.headers.set("Connection", "close")
        self.headers.set("User-Agent", "My Browser")

    def _request_page(self) -> str:
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
    
    def _request_file(self) -> str:
        try:
            with open(self.path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "Error: File not found"
        except Exception as e:
            return f"Error: {str(e)}"
