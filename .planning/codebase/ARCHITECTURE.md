<!-- refreshed: 2026-05-25 -->
# Architecture

**Analysis Date:** 2026-05-25

## System Overview

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                              Clients                                     │
├──────────────────────┬───────────────────────┬───────────────────────────┤
│   Browser SPA / TMA  │   Telegram (3 bots)   │   Telegram (RefereeBot)   │
│   `frontend/src/`    │   doers / customers   │   anonymous chat relay    │
└──────────┬───────────┴────────────┬──────────┴────────────┬──────────────┘
           │ HTTPS (REST)           │ Long polling          │ Long polling
           ▼                        ▼                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       nginx reverse proxy (`infra/nginx/nginx.conf`)     │
│              `/api/*` → backend:8000   `/` → frontend:80 (Vite build)    │
└──────────┬───────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│        FastAPI app (`backend/app/main.py` — uvicorn, port 8000)          │
│        Routers (`backend/app/api/v1/*.py`)                               │
│              auth · users · specialists · customers ·                    │
│              projects · applications · reviews · notifications           │
└──────────┬───────────────────────────────────────────────────────────────┘
           │  ALL business rules go through services
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│        Service layer (`backend/app/services/*.py`)                       │
│        auth · profiles · projects · applications · reviews ·             │
│        chat_relay · notifications · errors (DomainError taxonomy)        │
└──────────┬─────────────────────────────────────┬─────────────────────────┘
           │ async SQLAlchemy                    │ Redis pub/sub
           ▼                                     ▼
┌─────────────────────────────────┐   ┌──────────────────────────────────┐
│ Postgres 16                     │   │ Redis 7  channel `notify:{uid}`  │
│ ORM: `backend/app/models/*.py`  │   │ Producer: `services/notifications│
│ Repos: `backend/app/            │   │   .py::notify`                   │
│   repositories/*.py`            │   │ Consumers: `bots/common/         │
│ Migrations: `backend/alembic/`  │   │   notifications.py`              │
└─────────────────────────────────┘   └──────────┬───────────────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────────┐
                                  │ aiogram bots (3 processes)       │
                                  │ `bots/doers_bot/main.py`         │
                                  │ `bots/customers_bot/main.py`     │
                                  │ `bots/referee_bot/main.py`       │
                                  │ Shared deps: `app.*` package via │
                                  │ direct import (monorepo)         │
                                  └──────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| FastAPI app factory | CORS, rate-limit, `DomainError` handler, `/health`, mount `api/v1` | `backend/app/main.py` |
| API v1 router aggregator | Compose 8 domain routers under `/api/v1` | `backend/app/api/router.py` |
| Auth router | Email + Telegram initData login, refresh, logout | `backend/app/api/v1/auth.py` |
| Auth service | Token issue/rotate, bcrypt verify, Telegram HMAC verify | `backend/app/services/auth.py` |
| Projects service | Project lifecycle (DRAFT→OPEN→IN_PROGRESS→COMPLETED→ARCHIVED), specialist selection fan-out | `backend/app/services/projects.py` |
| Applications service | Apply / withdraw / list + direct offers | `backend/app/services/applications.py` |
| Reviews service | Mutual review + rating recompute on profile | `backend/app/services/reviews.py` |
| Profiles service | Upsert specialist / customer profile, soft-delete user | `backend/app/services/profiles.py` |
| Chat relay service | `get_or_open_thread`, `post_message` (anonymous customer↔specialist) | `backend/app/services/chat_relay.py` |
| Notifications service | Persist `Notification`, publish to `notify:{user_id}` Redis channel | `backend/app/services/notifications.py` |
| Domain errors | `DomainError`, `ConflictError`, `ForbiddenError`, `NotFoundError` | `backend/app/services/errors.py` |
| Repositories | Pure read/write helpers (no business rules) | `backend/app/repositories/*.py` |
| Models | SQLAlchemy 2.x async ORM + enums | `backend/app/models/*.py` |
| Schemas | Pydantic v2 request/response DTOs | `backend/app/schemas/*.py` |
| Core | Settings, async engine + `SessionLocal`, Redis client, deps, JWT + Telegram HMAC | `backend/app/core/*.py` |
| Seed | Project templates seeding script | `backend/app/seed/run.py` |
| DoersBot | Specialist DM bot + Mini App entry + push specialist-scoped notifications | `bots/doers_bot/main.py` |
| CustomersBot | Customer DM bot + Mini App entry + push customer-scoped notifications | `bots/customers_bot/main.py` |
| RefereeBot | FSM-driven anonymous relay between customer ↔ specialist on a project | `bots/referee_bot/main.py` |
| Bot shared lib | `SessionLocal`, tg→user lookup, chat_id lookup, notification subscriber | `bots/common/*.py` |
| nginx | Reverse proxy: `/api/*` → backend, `/` → frontend SPA, OpenAPI passthrough | `infra/nginx/nginx.conf` |
| SPA shell | Header/nav by role, theme toggle, persistent auth via Zustand | `frontend/src/app/Shell.tsx` |
| Router | Role-guarded routes under `/s/*` (specialist) and `/c/*` (customer) | `frontend/src/app/router.tsx` |
| HTTP client | `fetch` wrapper with auto refresh on 401 | `frontend/src/lib/api.ts` |

## Pattern Overview

**Overall:** Monorepo with a single shared Python package `backend/app/` (the "domain core") consumed in-process by both the FastAPI REST API and three aiogram bot workers. Frontend is an independent Vite-built React SPA served as a static site behind the same nginx as the API.

**Key Characteristics:**
- Single source of truth for business logic lives in `backend/app/services/` — both HTTP routers and bot handlers call the same functions (e.g., `services.projects.select_specialist`, `services.chat_relay.post_message`).
- Layered: `core` (infra) → `models` (ORM) → `repositories` (queries) → `services` (rules) → `api/v1` routers / bot handlers (transport).
- Async everywhere: SQLAlchemy 2.x async sessions, `asyncpg`, `redis.asyncio`, FastAPI async endpoints, aiogram async dispatcher.
- Decoupled notification fan-out: services persist a `Notification` row and publish JSON to Redis `notify:{user_id}`; bot processes psubscribe `notify:*` and DM the relevant Telegram chat.
- Three bot processes are physically separate containers (so each can poll a distinct Telegram token), but logically share the same domain code through Python imports.

## Layers

**`backend/app/core/` (infrastructure):**
- Purpose: Cross-cutting infra primitives — no domain knowledge.
- Location: `backend/app/core/`
- Contains: `config.py` (pydantic-settings), `db.py` (async engine + `SessionLocal` + `get_session` FastAPI dep), `redis.py` (singleton `Redis` client + `notify_channel(uid)` helper), `security.py` (bcrypt, JWT access/refresh, Telegram initData HMAC), `deps.py` (`current_user`, `SpecialistOnly`, `CustomerOnly`).
- Depends on: settings only.
- Used by: every other layer.

**`backend/app/models/` (ORM):**
- Purpose: SQLAlchemy 2.x mapped classes + domain enums (`UserRole`, `ProjectStatus`, `ApplicationStatus`, `ChatParty`).
- Location: `backend/app/models/`
- Contains: `user`, `telegram`, `profile` (specialist + customer + workplaces + portfolio links), `project`, `application` (+ `DirectOffer`), `chat` (`ChatThread`, `Message`), `notification`, `review`, `base`.
- Depends on: `core.db` (declarative `Base`).
- Used by: repositories, services, bots (bots import models directly for ad-hoc queries inside handlers).

**`backend/app/repositories/` (query helpers):**
- Purpose: Reusable read/write helpers (`get_user_by_email`, `get_project`, `find_thread`, etc.). No business rules.
- Location: `backend/app/repositories/`
- Depends on: models.
- Used by: services.

**`backend/app/services/` (business rules — the single source of truth):**
- Purpose: All state transitions, authorization, validation, and side-effect orchestration (DB write + notification publish in one transaction boundary).
- Location: `backend/app/services/`
- Pattern: pure async functions taking `(session, user, …)`; raise `DomainError` subclasses on rule violations; commit before returning.
- Depends on: repositories, models, `core.redis`, `core.security`.
- Used by: API v1 routers AND bot handlers (e.g., RefereeBot calls `services.chat_relay.get_or_open_thread` and `services.projects.select_specialist`).

**`backend/app/api/v1/` (HTTP transport):**
- Purpose: Thin routers — parse Pydantic DTOs, call a service, return another DTO. Routers add `/auth`, `/users`, `/specialists`, `/customers`, `/projects`, `/applications`, `/reviews`, `/notifications` under prefix `/api/v1`.
- Location: `backend/app/api/v1/`
- Depends on: services, schemas, `core.deps`.
- Used by: nginx (external HTTPS clients: SPA, TMA).

**`bots/` (Telegram transport):**
- Purpose: aiogram dispatchers — three independent processes, each long-polling a distinct bot token.
- Location: `bots/doers_bot/`, `bots/customers_bot/`, `bots/referee_bot/`, `bots/common/`
- Depends on: `app.services.*` for business rules, `app.models.*` for ad-hoc queries, `bots.common.db.SessionLocal` (its own session-maker so bots don't share FastAPI's request-scoped sessions).
- Used by: Telegram clients.

**`frontend/src/` (SPA):**
- Purpose: React 18 + Vite + react-router-dom + Zustand + Tailwind/shadcn-ui. Role-aware UI for specialists and customers; also runs inside Telegram Mini App.
- Location: `frontend/src/`
- Depends on: backend API only (`VITE_API_BASE_URL`, default `/api/v1`).

## Data Flow

### Primary Request Path (HTTP)

1. Browser/TMA sends `POST /api/v1/projects/{id}/select` with bearer token (`frontend/src/lib/api.ts:39`).
2. nginx proxies `/api/*` to `backend:8000` (`infra/nginx/nginx.conf:24`).
3. FastAPI resolves `current_user` via `HTTPBearer` + `decode_token` + `get_user` (`backend/app/core/deps.py:20`).
4. Router handler in `backend/app/api/v1/projects.py` calls `services.projects.select_specialist(session, user, project_id, specialist_id)` (`backend/app/services/projects.py:57`).
5. Service mutates `Application.status`, `Project.status`, `Project.selected_specialist_id`; rejects other pending applications; closes peer chat threads; emits four `notify(...)` calls; commits (`backend/app/services/projects.py:77`).
6. Each `notify()` persists a `Notification` row and `PUBLISH notify:{user_id}` JSON payload on Redis (`backend/app/services/notifications.py:30`).
7. Handler serializes `Project` back as `ProjectOut` Pydantic DTO; returns to client.

### Notification Fan-out Path (Async Push)

1. `backend.services.notifications.notify(...)` publishes `{id,type,payload}` JSON on Redis channel `notify:{user_id}` (`backend/app/services/notifications.py:32`).
2. Each bot process subscribed with `psubscribe("notify:*")` in `run_notification_loop` (`bots/common/notifications.py:31`).
3. Loop filters by per-bot allow-list (e.g., `SPECIALIST_NOTIFICATIONS` in `bots/doers_bot/main.py:52`).
4. Looks up `chat_id` via `bots.common.lookup.chat_id_for_user_id(uid, role=...)` joining `telegram_accounts` and filtering by role (`bots/common/lookup.py:12`).
5. Formats and DMs the user via `bot.send_message(chat_id, text)`.

### RefereeBot Relay Path

1. Customer hits `/start` → `update_chat_id` persists their Telegram `chat_id` (`bots/referee_bot/main.py:63`).
2. Customer picks open project → callback `proj:<uuid>` lists `PENDING` applications anonymously as `Chat #N` / `Select #N` (`bots/referee_bot/main.py:130`).
3. Customer clicks `chat:<project_id>:<specialist_id>` → `services.chat_relay.get_or_open_thread` upserts a `ChatThread` row; FSM transitions to `ChatState.in_thread` with `thread_id` in state data (`bots/referee_bot/main.py:168`).
4. Free-form text inside `in_thread` is captured by `on_text_in_thread`, which calls `services.chat_relay.post_message` (persists `Message` row with `sender_party`, returns counterparty `user_id`), then looks up the counterparty's `TelegramAccount.chat_id` and forwards the text with a generic `Customer:` / `Specialist:` label — identities never leak (`bots/referee_bot/main.py:259`).
5. `select:<project_id>:<specialist_id>` finalizes via `services.projects.select_specialist`, which closes peer threads and pushes accept/reject notifications.

**State Management:**
- Server: stateless aside from SQLAlchemy session per request (`get_session`) and singleton Redis connection.
- RefereeBot: in-memory aiogram `FSMContext` per (chat, user); only `thread_id` is kept.
- Frontend: Zustand `useAuthStore` persisted in `localStorage` as `doings-auth` (`frontend/src/stores/auth.ts:22`).

## Key Abstractions

**`DomainError` hierarchy:**
- Purpose: Carry HTTP-shaped errors out of pure services without coupling them to FastAPI.
- Examples: `backend/app/services/errors.py`
- Pattern: Subclasses set `status_code` (e.g., 403, 404, 409, 422); FastAPI global handler in `backend/app/main.py:40` converts to `JSONResponse`; bots catch and surface as alerts (`bots/referee_bot/main.py:181`).

**Service function signature:**
- Purpose: Uniform `(session: AsyncSession, user: User, …) -> Entity` shape so handlers and bots compose identically.
- Examples: every function in `backend/app/services/*.py`.

**Role enum + dependency:**
- Purpose: Centralize role gating.
- Examples: `UserRole` in `backend/app/models/user.py`; `require_role(*roles)` + `SpecialistOnly` / `CustomerOnly` aliases in `backend/app/core/deps.py:43`.

**Redis channel naming:**
- Purpose: One pub/sub channel per recipient user — bots filter consumer-side by notification type.
- Convention: `notify:{user_id}` produced by `notify_channel()` in `backend/app/core/redis.py:15`.

## Entry Points

**FastAPI:**
- Location: `backend/app/main.py` (`app = create_app()`)
- Triggers: uvicorn (`docker-compose.yml:54`: `uvicorn app.main:app --host 0.0.0.0 --port 8000`).
- Responsibilities: configure CORS, rate limiter, exception handler, mount `api_v1`.

**Bots (three independent processes):**
- Locations: `bots/doers_bot/main.py`, `bots/customers_bot/main.py`, `bots/referee_bot/main.py`
- Triggers: docker compose runs `python -m doers_bot.main` / `python -m customers_bot.main` / `python -m referee_bot.main` (`docker-compose.yml:56-66`).
- Responsibilities: bind aiogram `Dispatcher`, register handlers, run `start_polling` (DoersBot and CustomersBot also `gather` a Redis notification loop).

**SPA:**
- Location: `frontend/src/main.tsx` (mounts `<App />` into `#root`).
- Triggers: nginx serves Vite build artifacts; SPA loads `frontend/src/app/router.tsx` and routes by role.

**Seed:**
- Location: `backend/app/seed/run.py` (project templates).

**Alembic:**
- Location: `backend/alembic/` (single revision `20260525_0001_initial.py`); auto-runs at backend start when `RUN_MIGRATIONS_ON_START=1` (`docker-compose.yml:46`).

## Architectural Constraints

- **Threading:** Single-event-loop async. FastAPI under uvicorn workers; each bot is a single asyncio process. No worker threads, no Celery.
- **Sessions:** FastAPI uses `get_session` request-scoped dep (`backend/app/core/db.py:27`). Bots use their own `bots.common.db.SessionLocal` with `async with` blocks — never reuse FastAPI's `SessionLocal` from bot code.
- **Redis client:** Singleton lazily created in `app.core.redis.get_redis()`; safe across coroutines (`redis.asyncio`). Bots and API share the same module-level instance per process.
- **Notification publish is best-effort:** `notify()` swallows Redis exceptions so a Redis outage doesn't roll back a successful DB transaction (`backend/app/services/notifications.py:36`).
- **Auth duality:** Two auth flows for the same `User` table — email/password (`password_hash` set) and Telegram (`TelegramAccount` row linked, `password_hash` nullable). `login_telegram` requires `role` only on first-time signup.
- **Role-by-row:** A `User` has exactly one role (`UserRole.SPECIALIST` xor `UserRole.CUSTOMER`); switching roles is not supported. All service guards branch on `user.role`.
- **Project state machine:** `DRAFT → OPEN → IN_PROGRESS → COMPLETED → ARCHIVED`, plus `CANCELED` from DRAFT/OPEN. Enforced inside services with `ConflictError`.
- **Anonymity invariant (RefereeBot):** Forwarded messages must be labeled only as `Customer:` / `Specialist:` — never include user IDs, names, or usernames. Specialists in customer's applicant list are shown as `Chat #1`, `Chat #2` etc. (`bots/referee_bot/main.py:153`).

## Anti-Patterns

### Business logic in router or bot handler

**What happens:** Mutating models or checking ownership directly inside `backend/app/api/v1/*.py` or a bot callback.
**Why it's wrong:** Splits the rule set across HTTP and Telegram surfaces; bots and API will drift.
**Do this instead:** Add or extend a function in `backend/app/services/<domain>.py` and have both transports call it. See how `bots/referee_bot/main.py:201` reuses `services.projects.select_specialist`.

### Raising `HTTPException` from a service

**What happens:** Importing `fastapi.HTTPException` inside `backend/app/services/*.py`.
**Why it's wrong:** Services are shared with bots; FastAPI exceptions don't translate to Telegram and won't be caught uniformly.
**Do this instead:** Raise a `DomainError` subclass from `backend/app/services/errors.py`; FastAPI's global handler (`backend/app/main.py:40`) and bot try/except blocks both handle it.

### Sharing FastAPI's session from a bot

**What happens:** Importing `app.core.db.SessionLocal` inside `bots/`.
**Why it's wrong:** Couples bot lifetime to FastAPI's engine config; will fight `expire_on_commit` semantics tuned for request scope.
**Do this instead:** Use `bots.common.db.SessionLocal` inside `async with` blocks.

### Direct `bot.send_message` for cross-cutting notifications

**What happens:** Calling `bot.send_message` directly from a service to notify a user.
**Why it's wrong:** Services don't (and must not) hold an aiogram `Bot` instance; one service call may target multiple bots.
**Do this instead:** Call `services.notifications.notify(session, user_id, type_, payload)`. The right bot's `run_notification_loop` picks it up via type filter (`bots/doers_bot/main.py:52`).

### Querying models from a handler when a repository exists

**What happens:** Inlining `select(Project).where(...)` in router code.
**Why it's wrong:** Duplicates query logic; bypasses soft-delete checks like `project.deleted_at is not None`.
**Do this instead:** Use `app/repositories/*.py` (e.g., `repositories.projects.get_project`).

## Error Handling

**Strategy:** Services raise `DomainError` (or subclass: `ConflictError`/409, `ForbiddenError`/403, `NotFoundError`/404). FastAPI converts to JSON `{"detail": message}` via global handler; bots `try/except DomainError` and surface as `call.answer(message, show_alert=True)` or `message.answer(f"⚠️ {message}")`.

**Patterns:**
- Unique-constraint violations caught as `IntegrityError`, rolled back, and re-raised as `ConflictError` (e.g., `services/applications.py:35`, `services/reviews.py:47`).
- Auth failures use raw `HTTPException(401)` in `backend/app/core/deps.py` because auth is HTTP-only.
- Notification publish failures are swallowed (`services/notifications.py:36`).

## Cross-Cutting Concerns

**Logging:** stdlib `logging` configured at module level in `backend/app/main.py:16` and each bot's `main()`. Format: `%(asctime)s %(levelname)s %(name)s %(message)s`.

**Validation:** Pydantic v2 schemas in `backend/app/schemas/*.py`; FastAPI validates on the way in, services re-check authorization and state.

**Authentication:**
- HTTP: `HTTPBearer` → `decode_token` (JWT, type `access`) → `get_user` (`backend/app/core/deps.py:20`).
- Telegram initData: HMAC-SHA256 verification against `bot_token` in `backend/app/core/security.py::verify_telegram_init_data`; supports per-bot token lookup via `settings.all_bot_tokens` (`backend/app/services/auth.py:70`).
- Refresh tokens stored in `refresh_tokens` table with `jti`, `expires_at`, `revoked_at`; rotated on every `/auth/refresh`.

**Rate limiting:** `slowapi` `Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])` mounted in `backend/app/main.py:19`.

**CORS:** Configured from `settings.cors_origins_list` (`backend/app/main.py:33`).

---

*Architecture analysis: 2026-05-25*
