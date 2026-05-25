import hashlib
import hmac
import time

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
    verify_telegram_init_data,
)


def test_password_hash_roundtrip():
    h = hash_password("Sup3r-Pass!")
    assert verify_password("Sup3r-Pass!", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    tok = create_access_token("u-1", role="customer")
    decoded = decode_token(tok)
    assert decoded["sub"] == "u-1"
    assert decoded["type"] == "access"


def _make_init_data(bot_token: str, user: str = '{"id": 42, "username": "ada"}') -> str:
    fields = {"auth_date": str(int(time.time())), "user": user}
    data_check = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    h = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    return "&".join([f"{k}={v}" for k, v in fields.items()] + [f"hash={h}"])


def test_telegram_init_data_valid():
    token = "123456:ABC"
    data = _make_init_data(token)
    parsed = verify_telegram_init_data(data, token)
    assert parsed["user"] == '{"id": 42, "username": "ada"}'


def test_telegram_init_data_bad_hash():
    token = "123456:ABC"
    data = _make_init_data(token).replace("hash=", "hash=00")
    import pytest

    with pytest.raises(ValueError):
        verify_telegram_init_data(data, token)
