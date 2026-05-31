from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.router import api_v1
from app.core.config import get_settings
from app.services.errors import DomainError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


def create_app() -> FastAPI:
    app = FastAPI(
        title="Doings API",
        version="0.1.0",
        description="Telegram-native IT freelance marketplace",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def _domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "code": exc.code,
                "params": exc.params,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Map Pydantic errors to a stable ``validation.<type>`` code per field so
        # clients can render localized messages without parsing English text.
        errors = []
        for err in exc.errors():
            errors.append(
                {
                    "loc": list(err.get("loc", [])),
                    "type": err.get("type", "unknown"),
                    "code": f"validation.{err.get('type', 'unknown')}",
                    "msg": err.get("msg", ""),
                    "ctx": {k: _jsonable(v) for k, v in (err.get("ctx") or {}).items()},
                }
            )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation failed",
                "code": "validation.failed",
                "errors": errors,
            },
        )

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_v1)
    return app


def _jsonable(value: object) -> object:
    """Best-effort JSON-serialisable conversion for validation ctx values."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


app = create_app()
