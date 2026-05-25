class DomainError(Exception):
    """Raised by the service layer for business-rule violations."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(DomainError):
    def __init__(self, message: str = "Not found") -> None:
        super().__init__(message, status_code=404)


class ConflictError(DomainError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status_code=409)


class ForbiddenError(DomainError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status_code=403)
