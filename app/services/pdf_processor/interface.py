from abc import ABC, abstractmethod

class BaseTextExtractor(ABC):

    @abstractmethod
    def extract(self, file_bytes: bytes) -> str:
        pass

class BasePDFOptimizer(ABC):
    @abstractmethod
    def optimize(self, file_bytes: bytes) -> bytes:
        pass
    