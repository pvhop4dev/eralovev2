"""Storage DTOs (Data Transfer Objects)."""

from pydantic import BaseModel, Field


class PresignedUrlRequest(BaseModel):
    """Request body for generating a presigned upload URL."""

    file_name: str = Field(..., max_length=255, description="Original name of the file")
    content_type: str = Field(..., max_length=100, description="MIME type of the file (e.g. image/png)")
    file_type: str = Field(..., pattern="^(avatar|event)$", description="Type of storage object: 'avatar' or 'event'")


class PresignedUrlResponse(BaseModel):
    """Response body containing the presigned upload URL and public URL."""

    upload_url: str = Field(..., description="The presigned URL to PUT the file data to")
    file_url: str = Field(..., description="The final public URL where the file can be accessed")
