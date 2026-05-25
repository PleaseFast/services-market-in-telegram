# Codebase Structure

**Analysis Date:** 2026-05-25

## Directory Layout

```
services-market-in-telegram/
├── backend/                            # FastAPI app + shared domain package
│   ├── app/
│   │   ├── core/                       # Infra primitives (config, db, redis, security, deps)
│   │   ├── models/                     # SQLAlchemy 2.x ORM + enums
│   │   ├── schemas/                    # Pydantic v2 DTOs
│   │   ├── repositories/               # Query helpers (no business rules)
│   │   ├── services/                   # Business rules (single source of truth)
│   │   ├── api/
│   │   │   ├── router.py               # Aggregates v1 routers under /api/v1
│   │   │   └── v1/                     # auth, users, specialists, customers,
│   │   │                               # projects, applications, reviews, notifications
│   │   ├── seed/                       # Templates seeding script
│   │   └── main.py                     # FastAPI app factory + uvicorn entry
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/                   # Migration files (timestamp-prefixed)
│   ├── tests/                          # pytest suite (auth/projects/security)
│   ├── Dockerfile
│   └── pyproject.toml
│
├── bots/                               # Three aiogram bot processes + shared lib
│   ├── common/                         # Shared by all bots
│   │   ├── db.py                       # Bot-side async SessionLocal
│   │   ├── auth.py                     # get_user_by_tg, update_chat_id
│   │   ├── lookup.py                   # chat_id_for_user_id(role=...)
│   │   └── notifications.py            # Redis psubscribe → DM fan-out loop
│   ├── doers_bot/main.py               # Specialist assistant + Mini App entry
│   ├── customers_bot/main.py           # Customer assistant + Mini App entry
│   ├── referee_bot/main.py             # Anonymous customer↔specialist relay (FSM)
│   └── Dockerfile                      # Shared base image for all bot containers
│
├── frontend/                           # React 18 + Vite + Tailwind/shadcn SPA
│   ├── src/
│   │   ├── app/
│   │   │   ├── App.tsx                 # RouterProvider + QueryClient setup
│   │   │   ├── Shell.tsx               # Header/nav (role-aware), theme toggle, footer
│   │   │   └── router.tsx              # createBrowserRouter + RequireAuth guards
│   │   ├── components/
│   │   │   └── ui/                     # shadcn primitives (button, card, input, …)
│   │   ├── features/                   # One folder per domain
│   │   │   ├── landing/pages/          # LandingPage, NotFoundPage
│   │   │   ├── auth/
│   │   │   │   ├── api.ts              # login/register/refresh HTTP calls
│   │   │   │   └── pages/              # LoginPage, RegisterPage
│   │   │   ├── specialist/
│   │   │   │   ├── api.ts
│   │   │   │   └── pages/              # Dashboard, ProjectFeed, ProjectDetail,
│   │   │   │                           # SpecialistProfilePage, SpecialistArchive
│   │   │   ├── customer/
│   │   │   │   └── pages/              # Dashboard, CreateProject, CustomerProjects,
│   │   │   │                           # CustomerProjectDetail, SpecialistsCatalog
│   │   │   ├── projects/
│   │   │   │   ├── api.ts
│   │   │   │   └── types.ts
│   │   │   └── notifications/pages/    # NotificationsPage
│   │   ├── lib/
│   │   │   ├── api.ts                  # fetch wrapper + auto refresh on 401
│   │   │   ├── telegram.ts             # initData helpers
│   │   │   └── utils.ts                # cn() and misc
│   │   ├── stores/
│   │   │   └── auth.ts                 # Zustand auth store (persisted in localStorage)
│   │   ├── main.tsx                    # ReactDOM root
│   │   └── styles.css                  # Tailwind entry
│   ├── Dockerfile                      # Multi-stage: build → nginx:alpine static serve
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── infra/
│   ├── nginx/nginx.conf                # /api → backend:8000, / → frontend:80
│   └── postgres/init.sql               # Bootstrap (extensions, etc.)
│
├── .planning/                          # GSD planning artifacts
│   └── codebase/                       # This map (ARCHITECTURE.md, STRUCTURE.md, …)
├── .claude/                            # Slash-command + GSD workflow definitions
├── .agents/skills/                     # Project-installed skills (telegram-bot, shadcn, …)
│
├── docker-compose.yml                  # postgres, redis, backend, 3 bots, frontend, nginx
├── Makefile                            # Convenience targets (up/down/migrate/seed/test)
├── README.md
├── SKILL.md
├── .env.example                        # All required env vars (committed; .env is gitignored)
└── skills-lock.json
```

## Directory Purposes

**`backend/app/core/`:**
- Purpose: Cross-cutting infra — settings, DB engine, Redis client, security primitives, FastAPI deps.
- Contains: `config.py`, `db.py`, `redis.py`, `security.py`, `deps.py`.
- Key files: `backend/app/core/db.py`, `backend/app/core/security.py`, `backend/app/core/deps.py`.

**`backend/app/models/`:**
- Purpose: SQLAlchemy 2.x mapped classes; one module per domain aggregate plus `base.py`.
- Contains: `user.py` (+ `RefreshToken`, `UserRole`), `telegram.py`, `profile.py` (specialist + customer + workplaces + portfolio), `project.py` (+ `ProjectTemplate`, `ProjectStatus`), `application.py` (+ `DirectOffer`, `ApplicationStatus`), `chat.py` (`ChatThread`, `Message`, `ChatParty`), `notification.py`, `review.py`.
- Key files: `backend/app/models/__init__.py` (re-exports all classes).

**`backend/app/schemas/`:**
- Purpose: Pydantic v2 request/response DTOs. One module per domain mirroring models.
- Contains: `auth.py`, `user.py`, `profile.py`, `project.py`, `application.py`, `review.py`, `notification.py`, `common.py`.

**`backend/app/repositories/`:**
- Purpose: Reusable query helpers — keep router and service code free of raw `select(...)` boilerplate. No mutations of business rules.
- Contains: `users.py`, `specialists.py`, `projects.py`, `applications.py`, `chat.py`.

**`backend/app/services/`:**
- Purpose: All business rules. Both API routers and bot handlers call these.
- Contains: `auth.py`, `profiles.py`, `projects.py`, `applications.py`, `reviews.py`, `chat_relay.py`, `notifications.py`, `errors.py` (`DomainError` taxonomy).

**`backend/app/api/v1/`:**
- Purpose: HTTP transport. Thin routers — validate, call service, return DTO.
- Contains: `auth.py`, `users.py`, `specialists.py`, `customers.py`, `projects.py`, `applications.py`, `reviews.py`, `notifications.py`.
- Key file: `backend/app/api/router.py` (aggregator).

**`backend/app/seed/`:**
- Purpose: One-shot data seeding (project templates).
- Run: `python -m app.seed.run` (see `Makefile`).

**`backend/alembic/`:**
- Purpose: Schema migrations. Runs at backend start when `RUN_MIGRATIONS_ON_START=1`.
- Naming: `YYYYMMDD_NNNN_<slug>.py` (e.g., `20260525_0001_initial.py`).

**`backend/tests/`:**
- Purpose: pytest async test suite. Includes `conftest.py` (app + test DB fixtures).
- Files: `test_auth_api.py`, `test_project_flow.py`, `test_security.py`.

**`bots/common/`:**
- Purpose: Code reused by all three bots — DB session-maker, tg→user lookup, chat-id lookup, Redis notification fan-out loop.

**`bots/{doers,customers,referee}_bot/`:**
- Purpose: One module per Telegram bot. Each has `__init__.py` + `main.py` with an `async def main()` and `if __name__ == "__main__": asyncio.run(main())`.
- Run: `python -m doers_bot.main` (executed from `/app/bots` in the container).

**`frontend/src/features/<domain>/`:**
- Purpose: Domain-sliced UI code. Each feature is self-contained: `api.ts` (HTTP calls), `pages/*.tsx` (route components), optional `types.ts` (shared TS types).
- Pattern: never import from another feature's `pages/`; cross-feature reuse goes through `components/ui/`, `lib/`, or `stores/`.

**`frontend/src/components/ui/`:**
- Purpose: shadcn-ui primitives (button, card, input, label, textarea, badge). Generated by the `shadcn` CLI; safe to edit.

**`frontend/src/lib/`:**
- Purpose: Framework-agnostic helpers — `api.ts` (fetch wrapper with auto-refresh), `telegram.ts` (initData helpers), `utils.ts` (`cn` Tailwind merge).

**`frontend/src/stores/`:**
- Purpose: Zustand global stores. Currently only `auth.ts` (persisted as `doings-auth` in `localStorage`).

**`infra/nginx/`:**
- Purpose: Production nginx config. `/api/*` and `/docs|/redoc|/openapi.json` → backend; everything else → SPA.

**`infra/postgres/`:**
- Purpose: SQL run by the postgres container on first boot (extensions, etc.).

## Key File Locations

**Entry Points:**
- `backend/app/main.py` — FastAPI app factory (`app = create_app()`).
- `bots/doers_bot/main.py` — DoersBot (specialist).
- `bots/customers_bot/main.py` — CustomersBot (customer).
- `bots/referee_bot/main.py` — RefereeBot (anonymous chat relay).
- `frontend/src/main.tsx` — React DOM mount.
- `frontend/src/app/router.tsx` — route definitions.

**Configuration:**
- `.env.example` — required env vars (`DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `TG_*_BOT_TOKEN`, `TG_WEBAPP_URL`, `CORS_ORIGINS`, …).
- `docker-compose.yml` — all 7 services.
- `backend/pyproject.toml` — Python deps + ruff/mypy config.
- `backend/alembic.ini` — migration config.
- `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/tailwind.config.js`.
- `infra/nginx/nginx.conf`.

**Core Logic:**
- Business rules: `backend/app/services/` (every file).
- Domain model: `backend/app/models/`.
- HTTP transport: `backend/app/api/v1/`.
- Telegram transport: `bots/*/main.py`.

**Testing:**
- `backend/tests/conftest.py` — app + async DB fixtures.
- `backend/tests/test_*.py` — pytest cases.

## Naming Conventions

**Python files & modules (`backend/`, `bots/`):**
- `snake_case.py`, e.g., `chat_relay.py`, `applications.py`.
- One domain per module under `models/`, `schemas/`, `repositories/`, `services/`, `api/v1/`.
- Bot processes: `<role>_bot/main.py` invoked as `python -m <role>_bot.main`.

**Python classes:**
- `PascalCase`: `User`, `ChatThread`, `DomainError`, `SpecialistProfile`.
- Enums: `PascalCase` class with `UPPER_SNAKE` members (`UserRole.SPECIALIST`, `ProjectStatus.IN_PROGRESS`).
- Constants: module-level `UPPER_SNAKE` (`SPECIALIST_NOTIFICATIONS = {...}` in `bots/doers_bot/main.py:52`).

**Python functions:**
- `snake_case`, async by default.
- Service functions take `(session, user, …)` and return the domain entity or raise `DomainError`.
- Repository functions named `get_*`, `find_*`, `list_*`.
- Private helpers prefixed with `_` (e.g., `_owned_project`, `_recompute_rating`, `_issue_tokens`).

**TypeScript / React files (`frontend/`):**
- TSX components: `PascalCase.tsx` matching the default export (`LoginPage.tsx`, `CustomerProjectDetail.tsx`, `Shell.tsx`).
- Non-component modules: `camelCase.ts` (`api.ts`, `utils.ts`, `telegram.ts`, `auth.ts`).
- shadcn primitives: `kebab-or-lower.tsx` matching shadcn output (`button.tsx`, `card.tsx`).
- Hooks: `useXxx` (e.g., `useAuthStore`).
- Feature folders: lowercase singular noun by domain (`auth/`, `customer/`, `specialist/`, `projects/`, `notifications/`, `landing/`).
- Route paths: specialist area under `/s/*`, customer area under `/c/*`, shared under root (e.g., `/notifications`).

**Directories:**
- Python packages: `snake_case` (each contains `__init__.py`).
- Frontend: `camelCase`/lowercase nouns; no `kebab-case` anywhere in the source tree.

**Alembic migrations:**
- `YYYYMMDD_NNNN_<slug>.py` (e.g., `backend/alembic/versions/20260525_0001_initial.py`).

**Redis channels:**
- `notify:{user_id}` (produced by `app.core.redis.notify_channel`).

**Database tables:**
- Plural `snake_case` set by `__tablename__` in each model module.

## Where to Add New Code

**New API endpoint:**
1. Add Pydantic DTOs to `backend/app/schemas/<domain>.py`.
2. Add a service function in `backend/app/services/<domain>.py` (or new module). Raise `DomainError` subclasses on rule violations.
3. Add a route in `backend/app/api/v1/<domain>.py` calling the service.
4. If the router is new, register it in `backend/app/api/router.py`.
5. Add a pytest case to `backend/tests/`.

**New bot handler (or behavior that mirrors HTTP):**
- Reuse the same `backend/app/services/<domain>.<function>` the API uses. Do NOT reimplement rules in the handler.
- File: append to `bots/<bot>_bot/main.py`. If logic is shared across bots, put it in `bots/common/`.

**New domain model / table:**
1. Add `backend/app/models/<entity>.py` and re-export from `backend/app/models/__init__.py`.
2. Generate a migration in `backend/alembic/versions/` (manual or autogen).
3. Add a repository module if you'll have non-trivial queries.

**New notification type:**
1. Add constant to `NotificationType` class in `backend/app/services/notifications.py`.
2. Call `await notify(session, user_id, NotificationType.X, payload)` from the relevant service.
3. Add the type to the consuming bot's allow-list set (e.g., `SPECIALIST_NOTIFICATIONS` in `bots/doers_bot/main.py:52`) and extend its `format_notification` switch.

**New frontend feature:**
- Create `frontend/src/features/<domain>/` with `api.ts`, `pages/<Page>.tsx`, optional `types.ts`.
- Add routes to `frontend/src/app/router.tsx` under the appropriate `RequireAuth` block.
- Add nav links to `frontend/src/app/Shell.tsx` `links` array if the page should appear in the header nav.

**New shared UI component:**
- shadcn primitive: `frontend/src/components/ui/<name>.tsx` (or run shadcn CLI).
- App-specific composite: create `frontend/src/components/<Group>/<Name>.tsx` (group folder is optional).

**New shared utility:**
- Python: `backend/app/core/` for infra-touching, otherwise inline in the relevant `services/` module.
- TypeScript: `frontend/src/lib/`.

**New env var:**
- Add to `backend/app/core/config.py` (`Settings` class).
- Add to `.env.example` with a safe placeholder.
- Reference via `get_settings().YOUR_VAR`.

## Special Directories

**`.planning/`:**
- Purpose: GSD planning artifacts (codebase maps, phase plans, research).
- Generated: by GSD slash commands.
- Committed: yes.

**`.claude/`:**
- Purpose: Slash-command definitions, hooks, GSD workflow scripts and templates.
- Generated: managed by the GSD toolkit.
- Committed: yes (project-shared).

**`.agents/skills/`:**
- Purpose: Project-installed skill packs (`telegram-bot`, `telegram-mini-app`, `shadcn`, `sqlalchemy-alembic-…`, etc.).
- Generated: installed via skill manager; pinned in `skills-lock.json`.
- Committed: yes.

**`backend/alembic/versions/`:**
- Purpose: DB schema migration scripts.
- Generated: via `alembic revision` (manual or autogen).
- Committed: yes — never edit a migration that has been applied to a shared DB.

**`frontend/dist/`** (when present):
- Purpose: Vite production build output.
- Generated: yes (`npm run build`).
- Committed: no (gitignored).

**`pg-data` (docker volume):**
- Purpose: Postgres data directory.
- Generated: yes.
- Committed: no (named volume in `docker-compose.yml`).

---

*Structure analysis: 2026-05-25*
