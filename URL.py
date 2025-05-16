import socket
import ssl
import base64
from Headers import Headers
from abc import ABC, abstractmethod

class URL:
    def __init__(self, url: str):
        if url.startswith("data"):
            url = url[5:]
            if "," not in url:
                raise ValueError("Invalid data URL: missing comma")
            
            metadata, data = url.split(",", 1)
            is_base64 = ";base64" in metadata
            if is_base64:
                media_type = metadata.split(";base64")[0]
            else:
                media_type = metadata

            if not media_type:
                media_type = "text/plain"

            self.handler = DataURL(data, is_base64, media_type)
        else:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in ["http", "https", "file"]

            if self.scheme == "file":
                self.handler = FileURL(url)
            else:
                if "/" not in url:
                    url = url + "/"
                host, url = url.split("/", 1)
                path = "/" + url

                if self.scheme == "http":
                    port = 80
                elif self.scheme == "https":
                    port = 443

                if ":" in host:
                    host, port = host.split(":", 1)
                    port = int(port)

                self.handler = HttpURL(host, path, port, self.scheme)

    def request(self) -> str:
        return self.handler.request()
        
class URLHandler(ABC):
    @abstractmethod
    def request(self) -> str:
        pass
        
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
    
class FileURL(URLHandler):
    def __init__(self, path: str):
        self.path = path

    def request(self) -> str:
        try:
            with open(self.path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "Error: File not found"
        except Exception as e:
            return f"Error: {str(e)}"

class DataURL(URLHandler):
    def __init__(self, data: str, is_base64: bool = False, media_type: str = "text/plain"):
        self.data = data
        self.is_base64 = is_base64
        self.media_type = media_type

    def request(self) -> str:
        if self.is_base64:
            try:
                return base64.b64decode(self.data).decode("utf8")
            except Exception as e:
                return f"Error decoding base64 data: {str(e)}"
        else:
            return self.data
    
