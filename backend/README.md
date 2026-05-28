# Backend — FastAPI + SQLAlchemy

## Layout

```
app/
├── core/          config, db, security, deps
├── models/        SQLAlchemy 2.0 declarative models
├── schemas/       Pydantic v2 DTOs (separate IN / OUT shapes)
├── repositories/  pure data access (queries only)
├── services/      business logic — also reused by bot processes
├── api/v1/        FastAPI routers (auth, users, projects, …)
└── seed/          idempotent demo loader
alembic/           migrations
tests/             pytest (uses in-memory SQLite)
```

## Service boundary

`app/services/*.py` contains every business rule (lifecycle transitions,
permission checks, side-effects). Both the REST endpoints (`app/api/v1`) and
the bot processes (`/bots/*`) import from there — there is one place where a
"project is selected" or "review is recorded".

`DomainError` (+ subclasses `NotFoundError`, `ConflictError`,
`ForbiddenError`) lets services raise without depending on FastAPI; an
exception handler in `app/main.py` translates them to HTTP.

## Migrations

```bash
alembic upgrade head
alembic revision -m "add foo" --autogenerate   # then review by hand
```

Alembic uses the sync Postgres URL (`DATABASE_URL_SYNC`); the app uses the
async URL via asyncpg.

## ERD (textual)

```
users ──< specialist_profiles ──< specialist_workplaces
       │                       └─< specialist_portfolio_links
       ├─< customer_profiles
       ├─< telegram_accounts (1:1)
       ├─< refresh_tokens
       ├─< projects (as customer_id)
       │     ├─< applications
       │     ├─< direct_offers
       │     ├─< reviews
       │     └─< chat_threads ──< messages
       ├─< applications (as specialist_id)
       ├─< project_views (per-specialist view history; PK = (project_id, user_id))
       └─< notifications
```

All PKs are UUIDs (server-generated on Postgres via `gen_random_uuid()`,
Python-side `uuid4` on SQLite). Soft delete on `users`, `projects`,
`applications` via `deleted_at`.

## Auth

- Email/password: bcrypt via passlib; `/auth/register`, `/auth/login`.
- Telegram: `/auth/telegram` accepts raw `initData`, verifies HMAC with the
  configured bot token, links / creates user. Role is required on the first
  call only.
- Access + refresh JWTs. Refresh tokens are tracked in
  `refresh_tokens` and rotated on use; logout revokes a refresh `jti`.
- `app/core/deps.py` exposes `CurrentUser`, `SpecialistOnly`, `CustomerOnly`.

## Tests

```bash
pytest -q
```

Tests run against in-memory SQLite (aiosqlite). Coverage prioritises:

- password hashing + JWT roundtrip
- Telegram initData HMAC validation (positive + negative)
- register / login / `/auth/me`
- end-to-end project lifecycle (create → apply → select → complete →
  archive → reviews)

Heavier integration testing against Postgres can be added later by pointing
`DATABASE_URL` at the compose-managed DB.
