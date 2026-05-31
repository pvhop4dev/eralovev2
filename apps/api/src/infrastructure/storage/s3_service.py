"""AWS S3 Storage Service Implementation."""

import boto3
from botocore.config import Config
import structlog

from infrastructure.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class S3Service:
    """Service to handle interactions with AWS S3 / MinIO."""

    def __init__(self) -> None:
        s3_config = Config(signature_version="s3v4")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            config=s3_config,
        )
        self.bucket = settings.AWS_S3_BUCKET

    def generate_presigned_upload_url(
        self, key: str, content_type: str, expiry: int = 3600
    ) -> dict:
        """Generate a presigned URL to upload a file directly via PUT request.

        Args:
            key: The storage key (path) inside the bucket.
            content_type: The MIME type of the file.
            expiry: Expiration of the URL in seconds.

        Returns:
            Dict containing upload_url and file_url.
        """
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=expiry,
            )

            # Construct the public file URL
            if settings.AWS_ENDPOINT_URL:
                # Local dev: http://localhost:9000/eralove-media/key
                file_url = f"{settings.AWS_ENDPOINT_URL}/{self.bucket}/{key}"
            else:
                # Production AWS URL
                file_url = f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

            logger.info(
                "s3_presigned_url_generated",
                bucket=self.bucket,
                key=key,
                content_type=content_type,
            )
            return {
                "upload_url": url,
                "file_url": file_url,
            }
        except Exception as e:
            logger.error(
                "s3_presigned_url_failed",
                bucket=self.bucket,
                key=key,
                error=str(e),
            )
            raise e
