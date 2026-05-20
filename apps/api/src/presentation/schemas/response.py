"""Unified API Response Schemas.

All API responses follow this format: { data, meta, error }
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    page: int | None = None
    per_page: int | None = None
    total: int | None = None
    cursor: str | None = None
    has_next: bool = False


class ErrorDetail(BaseModel):
    """Error detail for error responses."""

    code: str
    message: str
    field: str | None = None
    details: list[dict] | None = None


class ApiResponse(BaseModel, Generic[T]):
    """Unified API response wrapper.

    Every endpoint returns this format:
    - Success: { data: T, meta: PaginationMeta | null, error: null }
    - Error:   { data: null, meta: null, error: ErrorDetail }
    """

    data: T | None = None
    meta: PaginationMeta | None = None
    error: ErrorDetail | None = None
