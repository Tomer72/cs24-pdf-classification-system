import os
import io
import logging
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials  
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.services.storage.interface import BaseStorage

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveStorage(BaseStorage):
    def __init__(self):
        self.creds = self._get_credentials()
        self.service = None
        
        self.root_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        
        if self.creds:
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("Google Drive service initialized successfully using User Credentials.")
        else:
            logger.critical("Google Drive auth failed. 'token.json' might be missing.")

    def _get_credentials(self):
        
        try:
            token_path = 'token.json'
            
            if os.path.exists(token_path):
                
                return Credentials.from_authorized_user_file(token_path, SCOPES)
            
            logger.error("token.json not found! Please run generate_token.py first.")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return None

    def upload_file(self, file_bytes: bytes, original_filename: str, metadata: Dict[str, Any]) -> str:
        if not self.service:
            logger.error("Drive service is not initialized.")
            return ""

        try:
            ext = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
            
            new_filename = (
                f"מועד {metadata.get('term', '?')} "
                f"סמסטר {metadata.get('semester', '?')} "
                f"{metadata.get('year', '????')}.{ext}"
            )

            logger.info(f"Preparing to upload: {new_filename}")

            institution_folder_id = self._get_or_create_folder(
                folder_name=metadata.get('institution', 'General Institution'), 
                parent_id=self.root_folder_id
            )
            
            degree_folder_id = self._get_or_create_folder(
                folder_name=metadata.get('degree', 'General Degree'), 
                parent_id=institution_folder_id  
            )
            
            course_folder_id = self._get_or_create_folder(
                folder_name=metadata.get('course_name', 'Unknown Course'), 
                parent_id=degree_folder_id
            )
            
            exams_folder_id = self._get_or_create_folder(
                folder_name="מבחנים", 
                parent_id=course_folder_id
            )

            
            if self._file_exists(new_filename, exams_folder_id):
                logger.warning(f"File '{new_filename}' already exists. Skipping upload.")
                return "exists"

            file_metadata = {
                'name': new_filename,
                'parents': [exams_folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_bytes),
                mimetype='application/pdf',
                resumable=True
            )

            logger.info(f"Uploading file to folder ID: {exams_folder_id}...")
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            link = file.get('webViewLink')
            logger.info(f"Upload successful! Link: {link}")
            return link

        except Exception as e:
            logger.error(f"Failed to upload to Drive: {e}", exc_info=True)
            return ""

    def _get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        
        try:
            query = (
                f"mimeType='application/vnd.google-apps.folder' "
                f"and name='{folder_name}' "
                f"and trashed=false"
            )
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query, 
                spaces='drive', 
                fields='files(id)'
            ).execute()
            
            items = results.get('files', [])

            if items:
                return items[0]['id']

            logger.info(f"Creating new folder: {folder_name}")
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id] if parent_id else []
            }
            
            folder = self.service.files().create(
                body=folder_metadata, 
                fields='id'
            ).execute()
            
            return folder.get('id')

        except Exception as e:
            logger.error(f"Error handling folder '{folder_name}': {e}")
            raise e

    def _file_exists(self, filename: str, parent_id: str) -> bool:
        
        try:
            query = (
                f"name='{filename}' "
                f"and '{parent_id}' in parents "
                f"and trashed=false"
            )
            results = self.service.files().list(
                q=query, 
                spaces='drive', 
                fields='files(id)'
            ).execute()
            return len(results.get('files', [])) > 0
        except Exception as e:
            logger.error(f"Error checking file existence: {e}")
            return False