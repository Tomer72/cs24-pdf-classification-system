import logging
import re
from .interface import BaseTextExtractor
from .local_extractor import PyMuPDFExtractor
from .cloud_extractor import GoogleVisionExtractor

logger = logging.getLogger(__name__)

class PDFProcessorManager:
    def __init__(self):
        self.local_extractor = PyMuPDFExtractor()
        self.cloud_extractor = GoogleVisionExtractor()

    def process(self, file_bytes: bytes) -> str:
        raw_text = self.extract_raw_text(file_bytes)
        clean_text = self.clean_text(raw_text)
        
        return clean_text

    def extract_raw_text(self, file_bytes: bytes) -> str:
        logger.info("Attempting local extraction (PyMuPDF)...")
        text = self.local_extractor.extract(file_bytes)

        clean_text_len = len(text.strip())

        if clean_text_len > 50:
            logger.info(f"Local extraction successful ({clean_text_len} chars extracted).")
            return text
        
        if clean_text_len == 0:
            logger.warning("Local extraction returned empty text. Switching to Cloud Vision OCR...")
        else:
            logger.warning(f"Local extraction returned only {clean_text_len} chars. Switching to Cloud Vision OCR...")   

        text = self.cloud_extractor.extract(file_bytes)

        if not text:
            logger.error("Both local and cloud extraction failed.")
            return ""

        return text

    def clean_text(self, raw_text: str) -> str:
        if not raw_text:
            return ""

        text = re.sub(r'\s+', ' ', raw_text)
        text = text.replace("''", '"').replace("״", '"').replace("‘", "'").replace("’", "'")
        return text.lower()