from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import parse_qsl

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_ctx.verify(password, hashed)


# --- JWT ---

def _encode(payload: dict[str, Any], ttl: timedelta) -> str:
    now = datetime.now(UTC)
    body = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(body, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_access_token(sub: str, role: str | None = None) -> str:
    return _encode(
        {"sub": sub, "role": role, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES),
    )


def create_refresh_token(sub: str) -> str:
    return _encode(
        {"sub": sub, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])


# --- Telegram initData validation ---

def verify_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> dict[str, Any]:
    """Verify Telegram Mini App initData per https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app.

    Returns parsed dict on success; raises ValueError on failure.
    """
    if not bot_token:
        raise ValueError("Bot token not configured")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("Missing hash")

    data_check_string = "\n".join(f"{k}={parsed[k]}" for k in sorted(parsed))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        raise ValueError("Bad hash")

    auth_date = int(parsed.get("auth_date", "0"))
    if auth_date and (datetime.now(UTC).timestamp() - auth_date) > max_age_seconds:
        raise ValueError("initData expired")

    return parsed
