from typing import Dict, Any
import logging
import re
from .interface import BaseValidator

logger = logging.getLogger(__name__)

class ExamValidator(BaseValidator):
    def validate(self, extracted_text: str, metadata: Dict[str, Any]) -> bool:

        if not extracted_text:
            logger.warning("Validation failed: Text is empty.")
            return False
            
        clean_text = self.clean_text(extracted_text)
        
        if not self.is_test_context(clean_text):
            logger.warning("Validation failed: Document does not appear to be an exam (missing keywords).")
            return False

        match_count = self.count_field_matches(clean_text, metadata)
        
        logger.info(f"Validation finished. Fields matched: {match_count}/5")

        return match_count >= 3

    def clean_text(self, raw_text: str) -> str:

        text = re.sub(r'\s+', ' ', raw_text)
        text = text.replace("''", '"').replace("״", '"').replace("‘", "'").replace("’", "'")
        return text.lower()

    def is_test_context(self, text: str) -> bool:

        keywords = ["מבחן", "מבחנים", "בחינה", "מועד", "סמסטר", "שנה", "נבחנים", "משך הבחינה", "הוראות"]
        count = 0

        for kw in keywords:
            
            if kw in text or kw[::-1] in text:
                count += 1
        
        return count >= 2

    def count_field_matches(self, text: str, metadata: Dict[str, Any]) -> int:
       
        count = 0
        fields_to_check = ["course_name", "semester", "year", "term", "degree"]
        
        for field in fields_to_check:
            value = str(metadata.get(field, "")).lower()
            if not value: 
                continue
            
            if value in text or value[::-1] in text:
                count += 1
                continue 
            
            if field == "course_name":
                words = value.split()
                if len(words) > 1:
                    
                    found_words = sum(1 for w in words if w in text or w[::-1] in text)
                    if found_words >= len(words) / 2:
                        count += 1
                        
        return count