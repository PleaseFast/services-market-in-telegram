# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Doings** — Telegram-native IT freelance marketplace MVP. Customers post projects, specialists apply, and the two sides chat anonymously via **RefereeBot** before a customer picks a performer. Two other bots (**DoersBot**, **CustomersBot**) launch the Mini App and deliver notifications.

## Common commands

All day-to-day operations go through the Makefile (which wraps `docker compose`):

```bash
make up          # build + start: postgres, redis, backend, 3 bots, frontend, nginx
make migrate     # alembic upgrade head (inside the backend container)
make seed        # idempotent: demo customer + specialist + 8 project templates
make down
make logs        # docker compose logs -f --tail=200
make test        # docker compose run --rm backend pytest -q
make fmt         # ruff format (backend) + prettier (frontend, if present)
make lint        # ruff check + eslint
make psql        # interactive psql shell into the postgres container
make backend-shell / make bot-shell
```

App lives at <http://localhost> (nginx → SPA + `/api/*` → FastAPI). API docs: <http://localhost/docs>.

### Running a single backend test

Tests run in the `backend` container against in-memory SQLite (aiosqlite). Use `docker compose run --rm backend pytest`:

```bash
docker compose run --rm backend pytest tests/test_project_flow.py::test_full_project_lifecycle -q
```

### Frontend dev (outside docker)

```bash
cd frontend && npm install && npm run dev   # Vite proxies /api → http://localhost:8000
```

### Demo credentials (after `make seed`)

`customer@demo.local` / `specialist@demo.local` — password `demo1234!`.

## Architecture — the parts that span files

The repository is a monorepo with **one shared business-logic core** consumed by both an HTTP API and three independent bot processes:

```
React SPA / Mini App ─HTTP─▶ FastAPI ─┐
                                      ├─▶ Postgres
3 aiogram bot processes ──────────────┘    Redis (pub/sub for notifications)
```

### The service-layer rule (critical)

`backend/app/services/*.py` is the **single source of truth for every business rule** — project lifecycle transitions, permission checks, rating recompute, application-to-selection flow, chat-relay persistence. Both the REST endpoints in `backend/app/api/v1/` and the bot handlers in `bots/*/main.py` call into these services. **Never duplicate a rule in a router or a bot handler.** Services raise `DomainError` / `NotFoundError` / `ConflictError` / `ForbiddenError` (defined in `backend/app/services/errors.py`); an exception handler in `backend/app/main.py` maps them to HTTP responses.

The layering goes: `core` → `models` (SQLAlchemy 2.0 async declarative) → `repositories` (pure queries, no business rules) → `services` (rules + side-effects) → `api/v1` routers + bot handlers.

### How bots share code with the backend

Bot processes install the backend as an editable Python package (`pip install -e /app/backend` in `bots/Dockerfile`) so they `from app.services.projects import select_specialist` rather than reimplementing it. The 3 bots run as 3 separate docker services (`doers_bot`, `customers_bot`, `referee_bot`) sharing the same Postgres + Redis.

### Notification fan-out

`app.services.notifications.notify(session, user_id, type, payload)` writes a `notifications` row **and** publishes a JSON message to Redis channel `notify:{user_id}`. Each bot runs `bots.common.notifications.run_notification_loop()` which `PSUBSCRIBE notify:*`, looks up the recipient's `chat_id` via `bots.common.lookup.chat_id_for_user_id(..., role=…)`, and DMs them — filtered by the bot's role audience (`SPECIALIST_NOTIFICATIONS` / `CUSTOMER_NOTIFICATIONS` sets in each bot's `main.py`). Best-effort: notify failures don't break the parent transaction.

### RefereeBot anonymous relay (the most cross-cutting flow)

`bots/referee_bot/main.py` is the most complete bot — an FSM (`ChatState.in_thread`) where:

1. Customer picks an open project → sees applicants labeled "Specialist #1/#2/…" (no names).
2. Tapping "Chat" calls `chat_relay.get_or_open_thread(project_id, customer_id, specialist_id)` which lazily inserts a `chat_threads` row.
3. Subsequent text in that state goes through `chat_relay.post_message`, persisted in `messages` and forwarded to the counterparty's stored `chat_id` with only a `Customer:` / `Specialist:` label — names are never leaked.
4. "Select" calls `projects.select_specialist(...)` which transitions the project to `in_progress`, rejects all other pending applications, and sets `closed=true` on the other threads.

### Auth — two paths, one user table

- **Email/password:** bcrypt via passlib, `/api/v1/auth/register` + `/auth/login`. Emails are lowercased before lookup.
- **Telegram:** `/api/v1/auth/telegram` accepts raw `initData`; `verify_telegram_init_data` in `backend/app/core/security.py` does the HMAC check against the relevant bot token (`bot` field: `doers`/`customers`/`referee`). Role is required on the **first** auth only; subsequent calls reuse the existing `users` row joined via `telegram_accounts.tg_user_id`.

Both paths issue an access JWT + a refresh JWT. Refresh tokens are tracked in `refresh_tokens` (jti + expiry + revoked_at) and **rotated on every `/auth/refresh`** — the old jti is marked revoked.

### Database — dialect-portable models, PG-specific migration

The models in `backend/app/models/` use `sa.Uuid(as_uuid=True)`, `sa.JSON`, `sa.String(254)` for email — **portable across SQLite (tests) and Postgres (prod)**. The Alembic migration `backend/alembic/versions/20260525_0001_initial.py` is the Postgres-specific source of truth: it uses `postgresql.UUID`, `postgresql.CITEXT`, `postgresql.JSONB`, `postgresql.ENUM(..., create_type=False)` + manual `.create(..., checkfirst=True)`, and `gen_random_uuid()` server defaults. If you add a new column, update **both** the model and the migration — there is no autogenerate workflow.

Tests rely on `Base.metadata.create_all` against aiosqlite (see `backend/tests/conftest.py`), so any new PG-only column type will break tests unless you abstract it.

## Frontend conventions

- Feature-first layout in `frontend/src/features/<domain>/` — each feature owns its `api.ts` (TanStack Query hooks), `pages/`, and `types.ts`.
- The single `apiClient` in `frontend/src/lib/api.ts` attaches the access token from the Zustand auth store and transparently handles 401 → refresh-token retry. **Use `http.get/post/put/patch/del` from `@/lib/api` — never call `fetch` directly in feature code.**
- Routing in `frontend/src/app/router.tsx` is role-guarded via `<RequireAuth role="specialist|customer">`. The auth store (`src/stores/auth.ts`) is persisted to localStorage under key `doings-auth`.
- Forms use React Hook Form + Zod resolver; Zod schemas live alongside the page.
- shadcn-style primitives are **inlined** in `src/components/ui/` (not installed via shadcn CLI). Follow the same `cva` + `cn` pattern when adding more.
- The SPA also serves as the Telegram Mini App: `App.tsx` calls `bootstrapTelegramAuth()` on boot, which reads `window.Telegram.WebApp.initData` (if present) and exchanges it for tokens. Both browsers and Telegram WebView use the same routes; pages should not branch on environment.

## Things to know before changing code

- **Role on Telegram first signup:** `/auth/telegram` requires a `role` field only for users that don't yet exist. Front-ends and bots that auto-bootstrap users (see `App.tsx` defaulting to `specialist`) need a way to let the user pick — accept this as a known UX gap rather than working around it elsewhere.
- **Project lifecycle states:** `draft → open → in_progress → completed → archived` (and `canceled` from draft/open). Transitions are enforced in `services/projects.py` — don't write status directly from a router.
- **Apply uniqueness:** `applications` has a unique `(project_id, specialist_id)`. The service catches `IntegrityError` and re-raises as `ConflictError`.
- **RefereeBot only relays text.** Photos/voice/files dropped on the floor — known limitation.

## Tests

Pytest + pytest-asyncio, in-memory aiosqlite. `backend/tests/conftest.py` overrides FastAPI's `get_session` dependency, rebuilds the schema per test, and exposes both a `session` and an httpx `client` fixture. Coverage today:

- `tests/test_security.py` — password hash, JWT roundtrip, Telegram initData HMAC (positive + negative).
- `tests/test_auth_api.py` — register / login / `/auth/me`.
- `tests/test_project_flow.py` — full lifecycle: register both roles → create profile → publish project → apply → double-apply rejected (409) → customer lists applicants → select specialist → project disappears from public feed → complete → reviews from both sides → archive.

No frontend tests yet. CI not wired.

## Where to look first

| You need to…                                  | Read                                                            |
| --------------------------------------------- | --------------------------------------------------------------- |
| Change project lifecycle rules                | `backend/app/services/projects.py`                              |
| Add an HTTP endpoint                          | `backend/app/api/v1/<domain>.py` + `backend/app/api/router.py`  |
| Add a column                                  | model in `backend/app/models/` **and** the alembic migration    |
| Send a new notification                       | `app.services.notifications.notify(...)` + extend each bot's `SPECIALIST_NOTIFICATIONS`/`CUSTOMER_NOTIFICATIONS` + `format_notification` |
| Extend RefereeBot                             | `bots/referee_bot/main.py` — note the FSM `ChatState.in_thread` |
| Add a frontend page                           | `frontend/src/features/<domain>/pages/` + route in `app/router.tsx` |

Deeper reference material lives in `.planning/codebase/` — generated by `/gsd:map-codebase`.
