from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from app.core.logger import setup_logger
import logging
from app.services.pdf_processor.cloud_extractor import GoogleVisionExtractor
from dotenv import load_dotenv

load_dotenv()
setup_logger()
app = FastAPI() 

pdf_extractor = GoogleVisionExtractor()
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

    extracted_text = pdf_extractor.extract(file_bytes)
    logger.info(f"File '{pdf_file.filename}' classified successfully for course: {course_name}")

    return {
        "status": "success",
        "filename": pdf_file.filename,
        "metadata_recieved": metadata,
        "extraction_result": {
            "length": len(extracted_text),
            "preview": extracted_text[:500],
            "full_text": extracted_text
        }
    }


    
