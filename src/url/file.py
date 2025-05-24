from .base import URLHandler

class FileURL(URLHandler):
    def __init__(self, path: str):
        self._path = path

    def request(self) -> str:
        try:
            with open(self._path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "Error: File not found"
        except Exception as e:
            return f"Error: {str(e)}" 