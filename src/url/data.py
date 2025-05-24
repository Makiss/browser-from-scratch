import base64
from .base import URLHandler

class DataURL(URLHandler):
    def __init__(self, data: str, is_base64: bool = False, media_type: str = "text/plain"):
        self._data = data
        self._is_base64 = is_base64
        self._media_type = media_type

    def request(self) -> str:
        if self._is_base64:
            try:
                return base64.b64decode(self._data).decode("utf8")
            except Exception as e:
                return f"Error decoding base64 data: {str(e)}"
        else:
            return self._data 