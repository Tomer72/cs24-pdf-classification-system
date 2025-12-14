from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from app.core.logger import setup_logger
import logging
from app.services.pdf_processor.manager import PDFProcessorManager
from app.services.validator.manager import ValidationManager
from app.services.storage.google_drive import GoogleDriveStorage
from dotenv import load_dotenv

load_dotenv()
setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI() 

pdf_manager = PDFProcessorManager()
validator_manager = ValidationManager()
google_drive_uploader = GoogleDriveStorage()

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
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        file_bytes = await pdf_file.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=400, detail="Failed to read file")
    
    
    if not file_bytes.startswith(b"%PDF"):
        logger.warning(f"Security Alert: User uploaded a fake pdf. filename: {pdf_file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file format (Not a PDF)")

    
    user_metadata = {
        "course_name": course_name,
        "semester": semester,
        "year": year,
        "term": term,
        "degree": degree
    }

    
    extracted_text = pdf_manager.process(file_bytes)
   
    validation_result = validator_manager.validate_process(extracted_text, user_metadata)

    
    if validation_result['status'] == 'failed':
        return {
            "status": "failed",
            "message": "Validation failed. Manual review required.",
            "ai_suggestion": validation_result.get("ai_suggestion")
        }

   
    final_metadata = validation_result.get("ai_data", user_metadata)
    
    logger.info(f"Uploading file with final metadata: {final_metadata}")

    drive_link = google_drive_uploader.upload_file(
        file_bytes=file_bytes, 
        original_filename=pdf_file.filename, 
        metadata=final_metadata
    )

  
    if not drive_link:
        raise HTTPException(status_code=500, detail="Upload to Drive failed")
    
    if drive_link == "exists":
         return {
            "status": "success",
            "message": "File already exists in Drive.",
            "data": final_metadata
        }

    return {
        "status": "success",
        "message": "File processed and uploaded successfully",
        "drive_link": drive_link,
        "final_metadata": final_metadata,
        "source": validation_result["source"] 
    }