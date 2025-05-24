from .http import HttpURL
from .file import FileURL
from .data import DataURL

class URL:
    def __init__(self, url: str):
        if url.startswith("data:"):
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

            self._handler = DataURL(data, is_base64, media_type)
        else:
            self._scheme, url = url.split("://", 1)
            assert self._scheme in ["http", "https", "file"]

            if self._scheme == "file":
                self._handler = FileURL(url)
            else:
                if "/" not in url:
                    url = url + "/"
                host, url = url.split("/", 1)
                path = "/" + url

                if self._scheme == "http":
                    port = 80
                elif self._scheme == "https":
                    port = 443

                if ":" in host:
                    host, port = host.split(":", 1)
                    port = int(port)

                self._handler = HttpURL(host, path, port, self._scheme)

    def request(self) -> str:
        return self._handler.request() 