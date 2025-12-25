from typing import Dict, Any, Optional
import os
import logging
import boto3
from app.services.storage.interface import BaseStorage
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class CloudflareStorage(BaseStorage):
    
    def __init__(self):
        self.account_id = os.getenv("R2_ACCOUNT_ID")
        self.access_key = os.getenv("R2_ACCESS_KEY")
        self.secret_key = os.getenv("R2_SECRET_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")

        self.s3_client = boto3.client(
            service_name = 's3',
            endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com",
            aws_access_key_id = self.access_key,
            aws_secret_access_key = self.secret_key,
            region_name = "auto"
        )

    def upload_file(self, file_bytes: bytes, original_filename: str, metadata: Dict[str, Any]) -> str:
        try:
            object_key = self.build_path(original_filename, metadata)
            logger.info(f"Uploading to R2: {object_key}")

            self.s3_client.put_object(
                Bucket = self.bucket_name,
                Key = object_key,
                Body = file_bytes,
                ContentType = "application/pdf"
            )

            return object_key

        except ClientError as e:
            logger.error(f"Failed to upload to R2: {e}")
            return None

    def build_path(self, filename: str, metadata: Dict[str, Any]) -> str:
        institution = metadata.get('institution', 'General').strip()
        course = metadata.get('course_name', 'Uncategorized').strip()
        degree = metadata.get('degree', 'Unknown').strip()

        ext = filename.split('.')[-1] if '.' in filename else 'pdf'

        new_filename = (
                f"מועד {metadata.get('term', '?')} "
                f"סמסטר {metadata.get('semester', '?')} "
                f"{metadata.get('year', '????')}.{ext}"
            )

        return f"{institution}/{degree}/{course}/מבחנים/{new_filename}"
