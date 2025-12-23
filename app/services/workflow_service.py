import logging
from typing import Dict, Any

from app.services.pdf_processor.manager import PDFProcessorManager
from app.services.validator.manager import ValidationManager
from app.services.storage.google_drive import GoogleDriveStorage

logger = logging.getLogger(__name__)

class DocumentProcessingService:
    def __init__(
            self,
            pdf_manager: PDFProcessorManager,
            validator_manager: ValidationManager,
            storage_service: GoogleDriveStorage
    ):
        self.pdf_manager = pdf_manager
        self.validator_manager = validator_manager
        self.storage_service = storage_service

    def process_and_upload(self, file_bytes: bytes, filename: str, user_metadata: Dict[str, Any]) -> Dict[str, Any]:

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

        if drive_link == "exists":
            return {
                "status": "success",
                "message": "File already exists.",
                "data": final_metadata,
                "link": None 
            }

        return {
            "status": "success",
            "message": "File processed and uploaded successfully",
            "drive_link": drive_link, 
            "final_metadata": final_metadata,
            "source": validation_result["source"] 
        }