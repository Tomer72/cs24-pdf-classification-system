from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseStorage(ABC):
    @abstractmethod
    def upload_file(self, file_bytes: bytes, original_filename: str, metadata: Dict[str, Any]) -> str:
        pass

