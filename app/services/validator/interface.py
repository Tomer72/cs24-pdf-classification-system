from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseValidator(ABC):

    @abstractmethod
    def validate(self, extracted_text: str, user_metadata: Dict[str, Any]) -> bool:
        pass

    
