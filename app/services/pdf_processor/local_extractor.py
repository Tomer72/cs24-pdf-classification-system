from .interface import BaseTextExtractor
import fitz
import logging

logger = logging.getLogger(__name__)

class PyMuPDFExtractor(BaseTextExtractor):
    def extract(self, file_bytes: bytes) -> str:
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                if doc.page_count > 0:
                    return doc[0].get_text()
            return ""
        except Exception as e:
            logger.error(f"PyMuPDF error: {e}")
            return ""
        