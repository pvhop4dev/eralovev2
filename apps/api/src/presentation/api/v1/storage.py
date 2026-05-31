"""Storage API Routes.

POST /api/v1/storage/presigned-url — Generate presigned S3 upload URL.
"""

from fastapi import APIRouter

from application.dtos.storage_dto import PresignedUrlRequest
from application.use_cases.storage.generate_presigned_url import GeneratePresignedUrlUseCase
from infrastructure.storage.s3_service import S3Service
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/presigned-url")
async def generate_presigned_url(
    body: PresignedUrlRequest,
    current_user: CurrentUser,
) -> dict:
    """Generate S3 presigned URL for direct client file uploads.

    Requires valid JWT authentication.
    """
    s3_service = S3Service()
    use_case = GeneratePresignedUrlUseCase(s3_service)
    response = await use_case.execute(body)

    return {
        "data": response.model_dump(),
        "meta": None,
        "error": None,
    }
