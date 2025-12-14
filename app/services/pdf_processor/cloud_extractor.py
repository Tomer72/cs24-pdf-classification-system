import fitz
from google.cloud import vision
import logging
from .interface import BaseTextExtractor

logger = logging.getLogger(__name__)

class GoogleVisionExtractor(BaseTextExtractor):
    def __init__(self):
        self._client = None 

    @property
    def client(self):
        if self._client is None:
            self._client = vision.ImageAnnotatorClient()
        return self._client

    def extract(self, file_bytes: bytes) -> str:
        logger.info("Starting Google Cloud Vision OCR extraction...")

        try:
            image_content = self.pdf_to_image_bytes(file_bytes)

            if not image_content:
                logger.warning("Could not convert PDF page to image (empty or invalid)")
                return ""
            
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)

            if response.error.message:
                logger.error(f"Google Vision API Error: {response.error.message}")
                return ""
            
            if response.text_annotations:
                text = response.text_annotations[0].description
                logger.info("Google vision extraction successful")
                return text
        
            logger.info("Google vision returned not text")
            return ""
        
        except Exception as e:
            logger.error(f"Cloud extraction failed: {e}")
            return ""
        
    def pdf_to_image_bytes(self, pdf_bytes: bytes) -> bytes:
        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                if doc.page_count < 1:
                    return None

                page = doc[0]
                pix = page.get_pixmap()
                return pix.tobytes("png")
        except Exception as e:
            logger.error(f"Failed to convert PDF to image for ocr: {e}")
            return None
