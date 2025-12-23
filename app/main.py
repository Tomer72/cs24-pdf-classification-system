from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from pydantic import BaseModel
from app.core.logger import setup_logger
import logging

from app.services.workflow_service import DocumentProcessingService
from app.dependencies import get_document_service

from dotenv import load_dotenv

load_dotenv()
setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI() 

class ExamMetadata(BaseModel):
    institution: str  
    course_name: str
    semester: str
    year: str
    term: str
    degree: str

    @classmethod
    def as_form(
        cls,
        institution: str = Form(...),
        course_name: str = Form(...),
        semester: str = Form(...),
        year: str = Form(...),
        term: str = Form(...),
        degree: str = Form(...)
    ):
        return cls(
            institution=institution,
            course_name=course_name,
            semester=semester,
            year=year,
            term=term,
            degree=degree
        )

@app.post("/upload-file")
async def upload_file(
    metadata: ExamMetadata = Depends(ExamMetadata.as_form), 
    pdf_file: UploadFile = File(...),
    service: DocumentProcessingService = Depends(get_document_service)
):

    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        file_bytes = await pdf_file.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=400, detail="Failed to read file")
    
    if not file_bytes.startswith(b"%PDF"):
        logger.warning(f"Security Alert: User uploaded a fake pdf. filename: {pdf_file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file format (Not a PDF)")

    user_metadata = metadata.model_dump() 

    try:
        result = service.process_and_upload(
            file_bytes=file_bytes,
            filename=pdf_file.filename,
            user_metadata=user_metadata
        )

        return result
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))