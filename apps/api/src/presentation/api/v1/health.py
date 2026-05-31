"""Health Check Endpoint.

GET /api/v1/health — returns server health status.
"""

from datetime import UTC, datetime

from fastapi import APIRouter

from presentation.schemas.response import ApiResponse

router = APIRouter(tags=["Health"])


class HealthResponse(ApiResponse):
    """Health check response."""

    pass


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Server status, version, and timestamp.
    """
    return {
        "data": {
            "status": "healthy",
            "version": "0.1.0",
            "service": "Eralove API",
            "timestamp": datetime.now(UTC).isoformat(),
        },
        "meta": None,
        "error": None,
    }
