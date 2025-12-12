import logging
from typing import Dict, Any
from .interface import BaseValidator
from .local_validator import ExamValidator
from .ai_validator import AIValidator

logger = logging.getLogger(__name__)

class ValidationManager:
    def __init__(self):
        self.local_validator: BaseValidator = ExamValidator()
        self.ai_validator: AIValidator = AIValidator()

    def validate_process(self, extracted_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        
        if self.local_validator.validate(extracted_text, metadata):
            logger.info("Local validation passed")
            return {
                "status": "success",
                "source": "local",
                "message": "File verified locally"
            }
        
        logger.warning("Local validation failed. switching to AI Validation")

        if self.ai_validator.validate(extracted_text, metadata):
            logger.info("AI Validation passed")

            ai_data = self.ai_validator.last_extracted_data

            return {
                "status": "success",
                "source": "ai",
                "ai_data": ai_data
            }

        logger.error("all validations failed")
        suggestion = self.ai_validator.last_extracted_data

        return {
            "status": "failed",
            "source": "none",
            "message": "Manual review required",
            "ai_suggestion": suggestion
        }