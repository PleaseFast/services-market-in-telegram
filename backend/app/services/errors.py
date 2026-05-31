"""Domain errors that carry stable codes for client-side translation.

Every error has a stable dotted ``code`` (e.g. ``"applications.already_applied"``)
plus optional interpolation ``params``. The FastAPI handler in ``app/main.py``
surfaces them as ``{"detail": <english fallback>, "code": ..., "params": ...}``
so frontends and bots can render localized text from the code while non-UI
clients still get a readable English string.

The ``message`` arg stays optional and acts as the dev-readable English
fallback. When omitted, the code itself is echoed in ``detail``.
"""

from __future__ import annotations


class DomainError(Exception):
    def __init__(
        self,
        code: str,
        *,
        status_code: int = 400,
        params: dict | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(message or code)
        self.code = code
        self.status_code = status_code
        self.params = dict(params or {})
        self.message = message or code


class NotFoundError(DomainError):
    def __init__(
        self,
        code: str = "common.not_found",
        *,
        params: dict | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(
            code, status_code=404, params=params, message=message or "Not found"
        )


class ConflictError(DomainError):
    def __init__(
        self,
        code: str = "common.conflict",
        *,
        params: dict | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(
            code, status_code=409, params=params, message=message or "Conflict"
        )


class ForbiddenError(DomainError):
    def __init__(
        self,
        code: str = "common.forbidden",
        *,
        params: dict | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(
            code, status_code=403, params=params, message=message or "Forbidden"
        )
