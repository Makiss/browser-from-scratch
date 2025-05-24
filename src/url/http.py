import socket
import ssl
from .base import URLHandler
from ..utils.headers import Headers
from urllib.parse import urljoin
from ..utils.cache import Cache
import gzip

MAX_REDIRECTS = 5
class HttpURL(URLHandler):
    _connections = {}
    _cache = Cache()

    def __init__(self, host: str, path: str, port: int, scheme: str):
        self._host = host
        self._path = path
        self._port = port
        self._scheme = scheme
        self._headers = Headers()
        self._set_default_headers()

    def request(self, redirect_count: int = 0) -> str:
        if (redirect_count >= MAX_REDIRECTS):
            raise Exception("Too many redirects")
        
        cache_key = f"{self._scheme}://{self._host}:{self._port}{self._path}"

        cached_response = self._cache.get(cache_key)
        if cached_response:
            return cached_response.content
        
        conn_key = (self._host, self._port)
        s = self._connections.get(conn_key)

        if s is None:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
            s.connect((self._host, self._port))
            if self._scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self._host)
        try:
            request = "GET {} HTTP/1.1\r\n".format(self._path)
            request += str(self._headers)
            request += "\r\n"
            s.send(request.encode("utf8"))

            response = s.makefile("rb", newline="\r\n")
            statusline = response.readline().decode("utf8")
            version, status, explanation = statusline.split(" ", 2)
            status = int(status)

            response_headers = {}
            while True:
                line = response.readline().decode("utf8")
                if line == "\r\n": 
                    break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()

            if 300 <= status < 400 and "location" in response_headers:
                location = response_headers["location"]
                new_url = self._create_redirect_url(location)
                return new_url.request(redirect_count + 1)

            if "transfer-encoding" in response_headers and "chunked" in response_headers["transfer-encoding"].lower():
                content = self._read_chunked_content(response)
            elif "content-length" in response_headers:
                content_length = int(response_headers["content-length"])
                content = response.read(content_length)
            else:
                content = response.read()
            
            if "content-encoding" in response_headers:
                content = self._decompress_content(content, response_headers["content-encoding"].lower())

            content_str = content.decode("utf8")

            self._connections[conn_key] = s

            if status == 200:
                self._cache.set(cache_key, content_str, response_headers)

            return content_str 
        
        except Exception as e:
            if conn_key in self._connections:
                del self._connections[conn_key]
            s.close()
            raise e
        
    def _set_default_headers(self) -> None:
        self._headers.set("Host", self._host)
        self._headers.set("User-Agent", "My Browser")
        self._headers.set("Accept-Encoding", "gzip")

    def _create_redirect_url(self, location: str) -> 'HttpURL':
        if not location.startswith(("http://", "https://")):
            base_url = f"{self._scheme}://{self._host}"
            if self._port not in (80, 443):
                base_url += f":{self._port}"
            location = urljoin(base_url, location)

        if location.startswith("http://"):
            scheme = "http"
            location = location[7:]
        elif location.startswith("https://"):
            scheme = "https"
            location = location[8:]
        else:
            raise ValueError(f"Invalid redirect URL: {location}")
        
        if "/" not in location:
            location = location + "/"
        host, path = location.split("/", 1)
        path = "/" + path

        if scheme == "http":
            port = 80
        elif scheme == "https":
            port = 443

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)
        
        return HttpURL(host, path, port, scheme)
    
    def _read_chunked_content(self, response) -> bytes:
        content = bytearray()
        while True:
            chunk_size_line = response.readline().decode("utf8").strip()
            if not chunk_size_line:
                continue

            chunk_size = int(chunk_size_line, 16)
            if chunk_size == 0:
                break

            chunk = response.read(chunk_size)
            content.extend(chunk)

            response.readline()

        return bytes(content) 
    
    def _decompress_content(self, content: bytes, encoding: str) -> bytes:
        if encoding == "gzip":
            return gzip.decompress(content)
        return content