"""Domain Exception → HTTP Response Handler.

Maps domain exceptions to appropriate HTTP status codes
and formats them into the unified ApiResponse error format.
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.exceptions import (
    BusinessRuleError,
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    TooManyRequestsError,
    UnauthorizedError,
    ValidationError,
)
from infrastructure.trace_context import get_trace_id

# Domain exception → HTTP status code mapping
_EXCEPTION_STATUS_MAP: dict[type[DomainError], int] = {
    NotFoundError: 404,
    ConflictError: 409,
    ForbiddenError: 403,
    UnauthorizedError: 401,
    ValidationError: 400,
    BusinessRuleError: 422,
    TooManyRequestsError: 429,
}


def _error_code(exc_type: type) -> str:
    """Convert exception class name to error code.

    NotFoundError → NOT_FOUND
    EmailAlreadyExistsError → EMAIL_ALREADY_EXISTS
    """
    name = exc_type.__name__
    if name.endswith("Error"):
        name = name[:-5]
    # Convert PascalCase to UPPER_SNAKE_CASE
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append("_")
        result.append(char.upper())
    return "".join(result)


async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Handle domain exceptions → JSON error response."""
    status = _EXCEPTION_STATUS_MAP.get(type(exc).__mro__[0], 500)

    # Walk up the MRO to find a matching status code
    for cls in type(exc).__mro__:
        if cls in _EXCEPTION_STATUS_MAP:
            status = _EXCEPTION_STATUS_MAP[cls]
            break

    return JSONResponse(
        status_code=status,
        content={
            "data": None,
            "meta": {"trace_id": get_trace_id()} if get_trace_id() else None,
            "error": {
                "code": _error_code(type(exc)),
                "message": str(exc),
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors → JSON error response."""
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append(
            {
                "field": field,
                "message": error["msg"],
            }
        )

    return JSONResponse(
        status_code=400,
        content={
            "data": None,
            "meta": {"trace_id": get_trace_id()} if get_trace_id() else None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": details,
            },
        },
    )
