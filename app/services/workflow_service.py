import logging
from typing import Dict, Any
import time

from app.services.pdf_processor.manager import PDFProcessorManager
from app.services.validator.manager import ValidationManager
from app.services.storage.google_drive import GoogleDriveStorage
from app.services.storage.cloudflare_r2 import CloudflareStorage

logger = logging.getLogger(__name__)

class DocumentProcessingService:
    def __init__(
            self,
            pdf_manager: PDFProcessorManager,
            validator_manager: ValidationManager,
            storage_service: CloudflareStorage
    ):
        self.pdf_manager = pdf_manager
        self.validator_manager = validator_manager
        self.storage_service = storage_service

    def process_and_upload(self, file_bytes: bytes, filename: str, user_metadata: Dict[str, Any]) -> Dict[str, Any]:

        start_time = time.time()

        processed_data = self.pdf_manager.process(file_bytes)
        extracted_text = processed_data["text"]
        optimized_bytes = processed_data["optimized_bytes"]

        validation_result = self.validator_manager.validate_process(extracted_text, user_metadata)

        if validation_result['status'] == 'failed':
            return {
                "status": "failed",
                "message": "Validation failed. Manual review required.",
                "ai_suggestion": validation_result.get("ai_suggestion")
            }

        final_metadata = validation_result.get("ai_data", user_metadata)
        
        logger.info(f"Uploading file with final metadata: {final_metadata}")

        drive_link = self.storage_service.upload_file(
            file_bytes = optimized_bytes, 
            original_filename = filename, 
            metadata = final_metadata
        )
    
        if not drive_link:
            raise Exception("Storage upload failed")

        end_time = time.time()
        
        logger.info(f"Process & Upload finished in {(end_time - start_time):.4f} seconds.")

        return {
            "status": "success",
            "message": "File processed and uploaded successfully",
            "drive_link": drive_link, 
            "final_metadata": final_metadata,
            "source": validation_result["source"] 
        }