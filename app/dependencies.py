from app.services.pdf_processor.manager import PDFProcessorManager
from app.services.validator.manager import ValidationManager
from app.services.storage.google_drive import GoogleDriveStorage
from app.services.workflow_service import DocumentProcessingService

_pdf_manager = PDFProcessorManager()
_validator_manager = ValidationManager()
_drive_storage = GoogleDriveStorage()

def get_document_service() -> DocumentProcessingService:
    return DocumentProcessingService(
        pdf_manager=_pdf_manager,
        validator_manager=_validator_manager,
        storage_service=_drive_storage
    )