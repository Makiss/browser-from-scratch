from .base import URLHandler
from .url import URL

class ViewSourceURL(URLHandler):
    def __init__(self, url: str):
        self.url = URL(url[12:])

    def request(self) -> str:
        return self.url.request()