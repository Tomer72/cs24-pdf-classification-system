import logging
from typing import Dict, Any
from .interface import BaseValidator
from app.services.validator.gemini_extractor import GeminiExtractor

logger = logging.getLogger(__name__)

class AIValidator(BaseValidator):
    def __init__(self):
     
        self.extractor = GeminiExtractor()

        self.last_extracted_data: Dict[str, Any] = {}

    def validate(self, extracted_text: str, metadata: Dict[str, Any]) -> bool:
  
        ai_data = self.extractor.extract(extracted_text)

        self.last_extracted_data = ai_data
        
        if not ai_data:
            logger.warning("AI extraction returned empty data or failed.")
            return False

        is_match = self.compare_metadata(metadata, ai_data)
        
        if is_match:
            logger.info("AI Validation passed successfully")
        else:
            logger.info("AI Validation failed comparison")

        return is_match
    
    @staticmethod
    def compare_metadata(user_data: Dict[str, Any], ai_data: Dict[str, Any]) -> bool:
        match_count = 0
        fields_to_check = ["course_name", "year", "semester", "term", "degree", "institution"]

        logger.info("Starting metadata comparison...")

        for field in fields_to_check:
            user_val = str(user_data.get(field, "")).strip()
            ai_val = str(ai_data.get(field, "")).strip()

            if not user_val or not ai_val:
                continue

            if user_val in ai_val or ai_val in user_val:
                match_count += 1
                logger.debug(f"Match found on field {field} : {user_val} <-> {ai_val}")
            else:
                logger.debug(f"Mismatch found on field {field}: user= {user_val}, ai = {ai_val}")

        logger.info(f"Total matches found: {match_count}")
        return match_count >= 3
    