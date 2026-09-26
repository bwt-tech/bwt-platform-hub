import boto3
from botocore.exceptions import ClientError
from loguru import logger

from app.src.core.exceptions import IntegrationError
from app.src.ports.s3_port import S3Port


class AWSS3Adapter(S3Port):
    def __init__(self, region_name: str):
        self.client = boto3.client("s3", region_name=region_name)

    def upload_content(self, bucket_name: str, file_name: str, content: str) -> None:
        try:
            logger.info(f"Uploading content {file_name} to bucket {bucket_name}")
            self.client.put_object(Bucket=bucket_name, Key=file_name, Body=content)
            logger.info(f"Content {file_name} uploaded successfully")
        except ClientError as e:
            logger.error(f"Failed to upload content {file_name}: {e}")
            raise IntegrationError(f"AWS S3 error: {str(e)}")
