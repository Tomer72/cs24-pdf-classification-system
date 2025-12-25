from app.services.pdf_processor.manager import PDFProcessorManager
from app.services.validator.manager import ValidationManager
from app.services.storage.google_drive import GoogleDriveStorage
from app.services.workflow_service import DocumentProcessingService
from app.services.storage.cloudflare_r2 import CloudflareStorage

_pdf_manager = PDFProcessorManager()
_validator_manager = ValidationManager()
_drive_storage = GoogleDriveStorage()
_r2_storage = CloudflareStorage()

def get_document_service() -> DocumentProcessingService:
    return DocumentProcessingService(
        pdf_manager=_pdf_manager,
        validator_manager=_validator_manager,
        storage_service=_r2_storage
    )