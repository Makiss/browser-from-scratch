from abc import ABC, abstractmethod

class URLHandler(ABC):
    @abstractmethod
    def request(self) -> str:
        pass 