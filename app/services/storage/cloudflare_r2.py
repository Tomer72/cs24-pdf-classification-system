from typing import Dict, Any, Optional
import os
import logging
import boto3
from app.services.storage.interface import BaseStorage

logger = logging.getLogger(__name__)

class CloudflareStorage(BaseStorage):
    
    def __init__(self):
        self.account_id = os.getenv("R2_ACCOUNT_ID")
        self.access_key = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        self.public_domain = os.getenv("R2_PUBLIC_DOMAIN")

        if not all([self.account_id, self.access_key, self.secret_key, self.bucket_name, self.public_domain]):
            logger.critical("Missing Cloudflare R2 credentials in .env")
            self.s3_client = None
        else:
            try:
                self.s3_client = boto3.client(
                    service_name='s3',
                    endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key
                )
                logger.info("Cloudflare R2 client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize R2 client: {e}")
                self.s3_client = None


    def upload_file(self, file_bytes: bytes, original_filename: str, metadata: Dict[str, Any]) -> str:
        pass
