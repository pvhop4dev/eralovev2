"""Eralove Domain Exceptions.

All business rule violations are expressed as domain exceptions.
These are mapped to HTTP status codes in the presentation layer.
"""


class DomainError(Exception):
    """Base for all domain errors."""

    def __init__(self, message: str = "A domain error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(DomainError):
    """Entity not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ConflictError(DomainError):
    """Duplicate resource."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message)


class ForbiddenError(DomainError):
    """No permission for this resource."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message)


class BusinessRuleError(DomainError):
    """Business logic violation."""

    def __init__(self, message: str = "Business rule violated"):
        super().__init__(message)


class UnauthorizedError(DomainError):
    """Authentication required or invalid."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class ValidationError(DomainError):
    """Domain-level validation error."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


# ── Specific Domain Errors ───────────────────────────────────

class UserNotFoundError(NotFoundError):
    """User not found."""

    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class CoupleNotFoundError(NotFoundError):
    """Couple not found or user is not matched."""

    def __init__(self, message: str = "You are not matched with anyone"):
        super().__init__(message)


class EventNotFoundError(NotFoundError):
    """Love event not found."""

    def __init__(self, message: str = "Event not found"):
        super().__init__(message)


class EmailAlreadyExistsError(ConflictError):
    """Email is already registered."""

    def __init__(self, message: str = "Email is already registered"):
        super().__init__(message)


class UsernameAlreadyExistsError(ConflictError):
    """Username is already taken."""

    def __init__(self, message: str = "Username is already taken"):
        super().__init__(message)


class AlreadyMatchedError(ConflictError):
    """User is already matched with someone."""

    def __init__(self, message: str = "You are already matched with someone"):
        super().__init__(message)


class AlreadyDeletedError(BusinessRuleError):
    """Entity has already been soft-deleted."""

    def __init__(self, message: str = "Resource is already deleted"):
        super().__init__(message)


class NotDeletedError(BusinessRuleError):
    """Entity is not deleted (cannot restore)."""

    def __init__(self, message: str = "Resource is not deleted"):
        super().__init__(message)


class RestoreWindowExpiredError(BusinessRuleError):
    """Restore window has expired."""

    def __init__(self, message: str = "Restore window has expired"):
        super().__init__(message)


class InvalidCredentialsError(UnauthorizedError):
    """Invalid email/password combination."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class TokenExpiredError(UnauthorizedError):
    """JWT token has expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class InvalidTokenError(UnauthorizedError):
    """JWT token is invalid."""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)
