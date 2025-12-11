from abc import ABC, abstractmethod

class BaseTextExtractor(ABC):

    @abstractmethod
    def extract(self, file_bytes: bytes) -> str:
        pass


    