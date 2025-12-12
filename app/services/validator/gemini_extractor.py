import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GeminiExtractor():
    def __init__(self):
        
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            logger.critical("GOOGLE_API_KEY not found in environment variables. AI extraction will fail.")
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                
                self.model = genai.GenerativeModel(
                    'gemini-3-pro-preview',
                    generation_config={"response_mime_type": "application/json"}
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                self.model = None

    def extract(self, text: str) -> Dict[str, Any]:
        
        if not self.model:
            logger.error("Gemini model is not initialized. Cannot extract metadata.")
            return {}

        if not text:
            logger.warning("Received empty text for AI extraction.")
            return {}

        logger.info("Sending text to Gemini for metadata extraction...")
        
        try:
            
            prompt = self.build_prompt(text)
     
            response = self.model.generate_content(prompt)
            
            extracted_data = json.loads(response.text)
            
            logger.info(f"Gemini extracted successfully: {extracted_data}")
            return extracted_data

        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response from Gemini.")
            return {}
        except Exception as e:
            logger.error(f"Error during Gemini extraction: {e}")
            return {}

    def build_prompt(self, text: str) -> str:
       
        text_preview = text[:1000]

        return f"""
        You are a helpful assistant that extracts metadata from exam PDFs. 
        
        Task: Extract the following fields from the exam text below.
        
        Required Fields and Formats:
        1. course_name: string
        2. semester: string (Options: ג, חורף, אביב, א, ב, קיץ)
        3. year: string (Format: YYYY e.g. 2025, OR Hebrew year e.g. תשפ״ה, תשפ״ו, תשפ״ג)
        4. term: string (Options: א, ב, ג, מיוחד)
        5. degree: string (Options: מדעי המחשב, הנדסת חשמל, הנדסת תעשייה וניהול)
        
        Exam Text:
        \"\"\"{text_preview}\"\"\"
        
        Instructions:
        - Return the result as a clean JSON object.
        - If a field is not found, return an empty string "".
        - Do not include Markdown formatting (```json).
        """