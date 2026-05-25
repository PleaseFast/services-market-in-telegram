from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_telegram_init_data,
)
from app.models.telegram import TelegramAccount
from app.models.user import RefreshToken, User, UserRole
from app.repositories.users import get_user_by_email, get_user_by_tg_id
from app.services.errors import ConflictError, DomainError

settings = get_settings()


async def _issue_tokens(session: AsyncSession, user: User) -> tuple[str, str]:
    access = create_access_token(str(user.id), role=user.role.value)
    refresh = create_refresh_token(str(user.id))
    payload = decode_token(refresh)
    session.add(
        RefreshToken(
            user_id=user.id,
            jti=payload["jti"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
        )
    )
    await session.flush()
    return access, refresh


async def register_email(session: AsyncSession, email: str, password: str, role: UserRole) -> tuple[User, str, str]:
    email = email.strip().lower()
    existing = await get_user_by_email(session, email)
    if existing:
        raise ConflictError("Email already registered")
    user = User(email=email, password_hash=hash_password(password), role=role)
    session.add(user)
    await session.flush()
    access, refresh = await _issue_tokens(session, user)
    await session.commit()
    return user, access, refresh


async def login_email(session: AsyncSession, email: str, password: str) -> tuple[User, str, str]:
    user = await get_user_by_email(session, email.strip().lower())
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise DomainError("Invalid credentials", status_code=401)
    access, refresh = await _issue_tokens(session, user)
    await session.commit()
    return user, access, refresh


async def login_telegram(
    session: AsyncSession,
    init_data: str,
    bot: str,
    role: UserRole | None,
) -> tuple[User, str, str]:
    token = settings.all_bot_tokens.get(bot)
    if not token:
        raise DomainError(f"Unknown bot '{bot}'", status_code=400)
    parsed = verify_telegram_init_data(init_data, token)
    user_field = parsed.get("user")
    if not user_field:
        raise DomainError("initData missing user field", status_code=400)
    tg_user = json.loads(user_field)
    tg_user_id = int(tg_user["id"])
    tg_username = tg_user.get("username")

    user = await get_user_by_tg_id(session, tg_user_id)
    if user is None:
        if role is None:
            raise DomainError("Role required for first-time signup", status_code=400)
        user = User(role=role)
        session.add(user)
        await session.flush()
        session.add(
            TelegramAccount(
                user_id=user.id,
                tg_user_id=tg_user_id,
                tg_username=tg_username,
                auth_date=datetime.fromtimestamp(int(parsed.get("auth_date", "0") or 0), tz=UTC),
            )
        )
        await session.flush()

    access, refresh = await _issue_tokens(session, user)
    await session.commit()
    return user, access, refresh


async def link_telegram_to_user(
    session: AsyncSession, user_id: UUID, tg_user_id: int, tg_username: str | None, chat_id: int | None
) -> TelegramAccount:
    res = await session.execute(
        select(TelegramAccount).where(TelegramAccount.user_id == user_id)
    )
    acc = res.scalar_one_or_none()
    if acc is None:
        acc = TelegramAccount(
            user_id=user_id,
            tg_user_id=tg_user_id,
            tg_username=tg_username,
            chat_id=chat_id,
            auth_date=datetime.now(UTC),
        )
        session.add(acc)
    else:
        acc.tg_user_id = tg_user_id
        acc.tg_username = tg_username
        if chat_id is not None:
            acc.chat_id = chat_id
    await session.flush()
    return acc


async def refresh_session(session: AsyncSession, refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token)
    except Exception as e:
        raise DomainError("Invalid refresh token", status_code=401) from e
    if payload.get("type") != "refresh":
        raise DomainError("Wrong token type", status_code=401)

    jti = payload["jti"]
    res = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    token_row = res.scalar_one_or_none()
    if token_row is None or token_row.revoked_at is not None:
        raise DomainError("Refresh token revoked", status_code=401)
    if token_row.expires_at < datetime.now(UTC):
        raise DomainError("Refresh token expired", status_code=401)

    token_row.revoked_at = datetime.now(UTC)
    user = await session.get(User, UUID(payload["sub"]))
    if user is None:
        raise DomainError("User not found", status_code=401)
    access, refresh = await _issue_tokens(session, user)
    await session.commit()
    return access, refresh


async def logout(session: AsyncSession, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        return
    res = await session.execute(select(RefreshToken).where(RefreshToken.jti == payload.get("jti", "")))
    row = res.scalar_one_or_none()
    if row is not None and row.revoked_at is None:
        row.revoked_at = datetime.now(UTC)
        await session.commit()
