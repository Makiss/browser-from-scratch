class Headers:
    def __init__(self):
        self.headers: dict[str, str] = {}
    
    def set(self, key: str, value: str) -> None:
        self.headers[key] = value
    
    def __str__(self) -> str:
        return "".join(f"{key}: {value}\r\n" for key, value in self.headers.items())

