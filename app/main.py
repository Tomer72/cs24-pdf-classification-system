from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from app.core.logger import setup_logger
import logging
from app.services.pdf_processor.manager import PDFProcessorManager
from app.services.validator.manager import ValidationManager
from dotenv import load_dotenv

load_dotenv()
setup_logger()
app = FastAPI() 

pdf_manager = PDFProcessorManager()
validator_manager = ValidationManager()
logger = logging.getLogger(__name__)

@app.post("/upload-file")
async def upload_file(
    course_name: str = Form(...),
    semester: str = Form(...),
    year: str = Form(...),
    term: str = Form(...),
    degree: str = Form(...),
    pdf_file: UploadFile = File(...)
):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code = 400, detail= "Invalid file type")
    
    try:
        file_bytes = await pdf_file.read()

    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read file")

    metadata = {"course_name": course_name,
                "semester": semester,
                "year": year,
                "term": term,
                "degree": degree
                }

    extracted_text = pdf_manager.process(file_bytes)
    is_valid = validator_manager.validate_process(extracted_text, metadata)

    logger.info(is_valid)


    
