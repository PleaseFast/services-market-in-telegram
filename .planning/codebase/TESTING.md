# Testing Patterns

**Analysis Date:** 2026-05-25

## Test Framework

**Runner:**
- `pytest >= 8.2` with `pytest-asyncio >= 0.23`
- Config: `backend/pyproject.toml` → `[tool.pytest.ini_options]`
  - `asyncio_mode = "auto"` (all `async def test_*` functions auto-run as asyncio)
  - `addopts = "-ra"` (summarize all non-passing outcomes)

**Assertion Library:**
- Plain `assert` statements (pytest rewrites them for rich diffs)

**HTTP Client (for API tests):**
- `httpx.AsyncClient` over `httpx.ASGITransport(app=app)` — drives the FastAPI app in-process, no network

**Database (for tests):**
- `aiosqlite` (in-memory SQLite, `sqlite+aiosqlite:///:memory:`) — portable, no Postgres needed in CI/dev
- Schema bootstrapped per test via `Base.metadata.create_all`

**Run Commands:**
```bash
cd backend
pytest                       # Run all tests
pytest -k project_flow       # Run a subset by keyword
pytest -x -vv                # Stop on first failure, verbose
```

## Test File Organization

**Location:**
- All tests under `backend/tests/`
- Separate from `app/` source (not co-located)

**Files present:**
- `backend/tests/conftest.py` — fixtures
- `backend/tests/test_security.py` — bcrypt + JWT + Telegram initData HMAC (positive and negative cases)
- `backend/tests/test_auth_api.py` — register / login / `me` endpoints
- `backend/tests/test_project_flow.py` — end-to-end project lifecycle

**Naming:**
- Files: `test_<area>.py`
- Functions: `test_<behaviour>` (e.g. `test_full_project_lifecycle`)

**Frontend:** No tests yet. No `vitest.config.*` / `jest.config.*` present.

## Test Structure

**Env setup BEFORE app import** (`backend/tests/conftest.py`):
```python
# Test env must be set BEFORE the app is imported.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-please-32-bytes-minimum"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["TG_REFEREE_BOT_TOKEN"] = "test:token"

from app.core.config import get_settings  # noqa: E402
get_settings.cache_clear()  # type: ignore[attr-defined]
```
Imports of `app.*` are deferred (`# noqa: E402`) because env vars must be in place before settings are first cached.

**Fresh schema per test:**
```python
@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()
```

**Session override via FastAPI `dependency_overrides`:**
```python
@pytest_asyncio.fixture
async def client(engine) -> AsyncIterator[AsyncClient]:
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def _override():
        async with SessionLocal() as s:
            yield s

    app.dependency_overrides[get_session] = _override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
```

The `engine` fixture rebuilds schema fresh for each test that requests `client` (since `client` depends on `engine`), giving full isolation without a per-test transaction-rollback trick.

## Patterns

**Test functions are `async`** under `asyncio_mode = "auto"`:
```python
@pytest.mark.asyncio
async def test_full_project_lifecycle(client):
    ...
```
The explicit `@pytest.mark.asyncio` is present but redundant with `asyncio_mode = "auto"` — either form works.

**Module-level helpers** for repeated workflows (`backend/tests/test_project_flow.py`):
```python
async def _register(client, email, role):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


def _auth(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}
```

**Assertion style:**
- Always check `status_code` first
- Include `r.text` as the assertion message when expecting 2xx so failures show server detail:
  ```python
  assert r.status_code == 201, r.text
  ```
- Then drill into `r.json()` for payload assertions

## Mocking

**Framework:** None used. The strategy is "real app + in-memory DB" rather than mocking collaborators.

**What is mocked:** Only the database connection (via dependency override + SQLite). HTTP, JWT, hashing all run for real.

**What NOT to mock:**
- The FastAPI app itself — drive it via `ASGITransport`
- Security primitives (bcrypt, JWT) — covered end-to-end in `test_security.py`

## Fixtures and Factories

**Fixtures** (`backend/tests/conftest.py`):
- `engine` — per-test in-memory async engine with schema created
- `session` — `AsyncSession` bound to the test engine (for repository/service-level tests)
- `client` — `httpx.AsyncClient` driving the FastAPI app with `get_session` overridden

**No factory library** (no `factory_boy`, no `polyfactory`). Test data is constructed inline as JSON dicts in each test. For shared registration flows, use module-private `_register` helpers.

**Location:** Fixtures live in `backend/tests/conftest.py`. Add new shared fixtures there.

## Coverage

**Requirements:** None enforced. No coverage tool configured.

**Current behavioural coverage:**
- **`test_security.py`** — bcrypt hash + verify roundtrip; JWT sign + decode roundtrip; Telegram `initData` HMAC validation (positive and negative cases)
- **`test_auth_api.py`** — `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- **`test_project_flow.py`** — full lifecycle:
  1. Register a customer and a specialist
  2. Specialist creates profile via `PUT /api/v1/specialists/me`
  3. Customer publishes a project (`publish: true`)
  4. Specialist applies via `POST /api/v1/projects/{id}/applications`
  5. Double-apply is rejected with `409`
  6. Customer lists applicants
  7. Customer selects the specialist (`POST /select-specialist/{id}`) → project moves to `in_progress`
  8. Project disappears from the public `GET /api/v1/projects` feed
  9. Customer marks complete → status `completed`
  10. Both customer and specialist post reviews
  11. Customer archives → status `archived`

## Test Types

**Unit tests:**
- `test_security.py` — pure functions (hash, JWT, HMAC), no DB needed

**API/integration tests:**
- `test_auth_api.py`, `test_project_flow.py` — drive real HTTP through `httpx.AsyncClient` against the FastAPI app with an in-memory DB

**E2E tests:** Not used (no browser/Telegram WebApp harness).

**Frontend tests:** Not yet wired.

## Common Patterns

**Async API call:**
```python
r = await client.post(
    f"/api/v1/projects/{project_id}/applications",
    headers=_auth(specialist),
    json={"cover_letter": "pick me"},
)
assert r.status_code == 201, r.text
```

**Negative-case testing:**
```python
# specialist cannot apply twice
r = await client.post(
    f"/api/v1/projects/{project_id}/applications",
    headers=_auth(specialist),
    json={"cover_letter": "again"},
)
assert r.status_code == 409
```

**Cross-resource invariant check:**
```python
# public feed should no longer contain the project
r = await client.get("/api/v1/projects")
assert all(p["id"] != project_id for p in r.json()["items"])
```

**Auth header construction:** Use the `_auth(token)` helper rather than inlining the `Authorization` dict.

## CI

Not yet wired. No `.github/workflows/`, no `.gitlab-ci.yml` detected. When added, the recommended baseline is:
```bash
cd backend
pip install -e ".[dev]"
ruff check .
pytest
```

---

*Testing analysis: 2026-05-25*
