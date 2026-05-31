from __future__ import annotations

import pytest

from app.core.i18n import DEFAULT, SUPPORTED, normalize, parse_accept_language


def test_normalize_supported_languages():
    assert normalize("ru") == "ru"
    assert normalize("en") == "en"
    assert normalize("ru-RU") == "ru"
    assert normalize("en_US") == "en"
    assert normalize("EN") == "en"


def test_normalize_unknown_falls_back_to_default():
    assert DEFAULT == "ru"
    assert normalize(None) == "ru"
    assert normalize("") == "ru"
    assert normalize("fr") == "ru"
    assert normalize("zh-CN") == "ru"


def test_parse_accept_language_picks_first_supported():
    assert parse_accept_language("ru-RU,ru;q=0.9,en;q=0.8") == "ru"
    assert parse_accept_language("en-GB,en;q=0.9") == "en"
    # Unsupported leading entry → first supported wins.
    assert parse_accept_language("fr,en") == "en"
    # No supported entry → DEFAULT.
    assert parse_accept_language("fr,de") == "ru"
    assert parse_accept_language(None) == "ru"


def test_supported_contract():
    assert "ru" in SUPPORTED
    assert "en" in SUPPORTED


@pytest.mark.asyncio
async def test_language_endpoints_default_and_update(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "lang@example.com", "password": "secret12345", "role": "customer"},
    )
    res = await client.post(
        "/api/v1/auth/login", json={"email": "lang@example.com", "password": "secret12345"}
    )
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/users/me/language", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"language": "ru"}

    res = await client.patch(
        "/api/v1/users/me/language", headers=headers, json={"language": "en"}
    )
    assert res.status_code == 200
    assert res.json() == {"language": "en"}

    res = await client.get("/api/v1/users/me/language", headers=headers)
    assert res.json() == {"language": "en"}


@pytest.mark.asyncio
async def test_language_endpoint_rejects_unsupported(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "lang2@example.com", "password": "secret12345", "role": "customer"},
    )
    res = await client.post(
        "/api/v1/auth/login", json={"email": "lang2@example.com", "password": "secret12345"}
    )
    token = res.json()["access_token"]
    res = await client.patch(
        "/api/v1/users/me/language",
        headers={"Authorization": f"Bearer {token}"},
        json={"language": "fr"},
    )
    assert res.status_code == 400
    body = res.json()
    assert body["code"] == "users.language_unsupported"
    assert body["params"]["language"] == "fr"


@pytest.mark.asyncio
async def test_error_response_shape_includes_code_and_params(client):
    # Trigger a domain error that we can recognise by code: duplicate email.
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "secret12345", "role": "customer"},
    )
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "secret12345", "role": "customer"},
    )
    assert res.status_code == 409
    body = res.json()
    assert body["code"] == "auth.email_taken"
    assert body["detail"] == "Email already registered"
    assert body["params"] == {}


@pytest.mark.asyncio
async def test_validation_error_shape(client):
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "x", "role": "customer"},
    )
    assert res.status_code == 422
    body = res.json()
    assert body["code"] == "validation.failed"
    assert isinstance(body["errors"], list)
    assert all("code" in err and err["code"].startswith("validation.") for err in body["errors"])


@pytest.mark.asyncio
async def test_templates_accept_language_returns_localized(client, session):
    # Seed a canonical template + ru translation directly.
    from app.models.project import ProjectTemplate, ProjectTemplateTranslation

    template = ProjectTemplate(
        title="Landing page for SaaS product",
        category="Frontend",
        description_template="English description",
    )
    session.add(template)
    await session.flush()
    session.add(
        ProjectTemplateTranslation(
            template_id=template.id,
            locale="ru",
            title="Лендинг для SaaS-продукта",
            description="Русское описание",
        )
    )
    await session.commit()

    res = await client.get("/api/v1/projects/templates", headers={"Accept-Language": "ru-RU"})
    assert res.status_code == 200
    rows = res.json()
    assert any(r["title"] == "Лендинг для SaaS-продукта" for r in rows)

    res = await client.get("/api/v1/projects/templates", headers={"Accept-Language": "en-US"})
    rows = res.json()
    assert any(r["title"] == "Landing page for SaaS product" for r in rows)


@pytest.mark.asyncio
async def test_templates_fallback_for_missing_translation(client, session):
    from app.models.project import ProjectTemplate

    template = ProjectTemplate(
        title="Only English Template",
        category="Backend",
        description_template="English-only description",
    )
    session.add(template)
    await session.commit()

    res = await client.get(
        "/api/v1/projects/templates", headers={"Accept-Language": "ru-RU"}
    )
    assert res.status_code == 200
    rows = res.json()
    match = next(r for r in rows if r["title"] == "Only English Template")
    assert match["description_template"] == "English-only description"


def test_category_label_returns_localized():
    from app.core.categories import label_for

    assert label_for("Frontend", "ru") == "Фронтенд"
    assert label_for("Frontend", "en") == "Frontend"
    assert label_for("Frontend", "fr") == "Фронтенд"  # falls back to ru default
    assert label_for("Other", "ru") == "Другое"


def test_suggest_category_works_on_russian_text():
    from app.core.categories import suggest_category

    assert suggest_category("Сделать телеграм-бота для FAQ") == "Bots"
    assert suggest_category("Хочу лендинг для стартапа") == "Frontend"
