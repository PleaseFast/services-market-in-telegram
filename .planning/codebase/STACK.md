# Technology Stack

**Analysis Date:** 2026-05-25

## Languages

**Primary:**
- Python 3.12 — Backend API (`backend/app/`) and bots (`bots/`); `requires-python = ">=3.12"` in both `backend/pyproject.toml` and `bots/pyproject.toml`
- TypeScript 5.6 — Frontend SPA / Telegram Mini App (`frontend/src/`); strict mode enabled in `frontend/tsconfig.json`

**Secondary:**
- SQL — Postgres bootstrap extensions (`infra/postgres/init.sql`) and Alembic migrations (`backend/alembic/versions/`)
- Bash — Backend container entrypoint (`backend/docker-entrypoint.sh`), Makefile targets (`Makefile`)
- Nginx configuration — `infra/nginx/nginx.conf`, `frontend/nginx.conf`

## Runtime

**Environment:**
- CPython 3.12 (image: `python:3.12-slim`) — backend (`backend/Dockerfile:1`) and all three bots (`bots/Dockerfile:1`)
- Node.js 20 alpine — frontend build stage only (`frontend/Dockerfile:1`); production serving is static via nginx
- Nginx 1.27 alpine — frontend static server (`frontend/Dockerfile:9`) and edge reverse proxy (`docker-compose.yml:76`)
- PostgreSQL 16 alpine — primary datastore (`docker-compose.yml:19`)
- Redis 7 alpine — pub/sub + ephemeral state (`docker-compose.yml:36`)

**Package Managers:**
- pip (Python) — both `backend` and `bots` installed editable via `pip install -e` (`backend/Dockerfile:17`, `bots/Dockerfile:16-20`)
- npm (Node) — `frontend/package.json`; install uses `--legacy-peer-deps` (`frontend/Dockerfile:5`)
- Lockfile: `package-lock.json` is referenced optionally in `frontend/Dockerfile:4` (`package-lock.json*`); no Python lockfile (pip directly resolves from `pyproject.toml`)

## Frameworks

**Backend Core:**
- FastAPI `>=0.115` — HTTP API; instantiated in `backend/app/main.py:23`
- Uvicorn `>=0.30` (`[standard]` extras) — ASGI server; container CMD `uvicorn app.main:app --host 0.0.0.0 --port 8000` (`backend/Dockerfile:29`, `docker-compose.yml:54`)
- SQLAlchemy `>=2.0.30` (async) — ORM; async engine via `create_async_engine` (`backend/app/core/db.py:13`)
- Pydantic `>=2.7` + `pydantic-settings >=2.3` — request/response schemas and settings (`backend/app/core/config.py`)
- Alembic `>=1.13` — schema migrations (`backend/alembic/`); driven by sync URL `DATABASE_URL_SYNC` in `backend/alembic/env.py:17`
- slowapi `>=0.1.9` — rate limiting middleware (`backend/app/main.py:8`, default `120/minute`)
- PyJWT `>=2.9` — HS256 JWT issuance/verification (`backend/app/core/security.py:10`)
- passlib `>=1.7.4` with `bcrypt` extra + `bcrypt >=4.0.1` — password hashing (`backend/app/core/security.py:11,16`)
- python-multipart `>=0.0.9` — form parsing (file/avatar URL uploads)
- email-validator `>=2.2` — Pydantic `EmailStr` support
- httpx `>=0.27` — outbound HTTP (currently unused for SaaS calls; available for future integrations)

**Bots Core:**
- aiogram `>=3.10` — Telegram Bot framework (long-polling Dispatcher); one process per bot (`bots/doers_bot/main.py:8`, `bots/customers_bot/main.py`, `bots/referee_bot/main.py:9`)
- The `bots` package depends on `doings-backend` (`bots/pyproject.toml:8`) — bots import `app.core`, `app.models`, `app.services` directly so business logic is shared

**Database Drivers:**
- asyncpg `>=0.29` — async Postgres driver used by FastAPI (`postgresql+asyncpg://...`)
- psycopg `>=3.2` (binary) — sync Postgres driver used by Alembic (`postgresql+psycopg://...`)
- redis `>=5.0` (`redis.asyncio.Redis`) — async Redis client (`backend/app/core/redis.py:1`)

**Testing:**
- pytest `>=8.2` + pytest-asyncio `>=0.23` (mode `auto`, configured in `backend/pyproject.toml:50`)
- anyio `>=4.4`
- aiosqlite `>=0.20` — in-memory SQLite for tests
- No frontend test runner is configured

**Build/Dev (Backend):**
- Ruff `>=0.6` — lint + format; line length 100, target `py312`, rules `E,F,I,B,UP,W` (`backend/pyproject.toml:41-47`)

**Frontend Core:**
- React 18.3 + React DOM 18.3
- Vite 5.4 (`frontend/vite.config.ts`); dev server binds `0.0.0.0:5173`, proxies `/api` → `http://localhost:8000`
- `@vitejs/plugin-react` 4.3
- React Router 6.27 (`react-router-dom`)
- TanStack Query 5.59 (`@tanstack/react-query`) — server state cache
- Zustand 4.5 — client state (e.g. `useAuthStore` in `frontend/src/stores/`)
- React Hook Form 7.53 + `@hookform/resolvers` 3.9
- Zod 3.23 — schema validation, wired into RHF via the resolver
- Tailwind CSS 3.4 + PostCSS 8.4 + autoprefixer 10.4; dark mode `class`; CSS variables for theme tokens (`frontend/tailwind.config.ts`)
- Radix UI primitives: `@radix-ui/react-dialog`, `react-dropdown-menu`, `react-label`, `react-select`, `react-slot`, `react-tabs` (shadcn/ui foundation)
- shadcn/ui pattern with `class-variance-authority` 0.7, `clsx` 2.1, `tailwind-merge` 2.5
- `lucide-react` 0.451 — icon set
- TypeScript 5.6, ESLint 9.12, Prettier 3.3 (dev)
- Telegram Web App SDK loaded directly from CDN: `<script src="https://telegram.org/js/telegram-web-app.js">` (`frontend/index.html:8`)

## Key Dependencies

**Critical:**
- `fastapi` — entire HTTP surface
- `sqlalchemy[asyncio]` + `asyncpg` — only path to Postgres at runtime
- `aiogram` — only Telegram interaction layer
- `redis.asyncio` — pub/sub fan-out for notifications (`backend/app/services/notifications.py`, `bots/common/notifications.py`)
- `pyjwt` + `passlib[bcrypt]` — auth foundation
- `slowapi` — request throttling (in-process; will need Redis backend to scale beyond one API replica)
- `@tanstack/react-query` — every API call from the SPA flows through it
- `zustand` — auth token storage (`useAuthStore`)

**Infrastructure:**
- `psycopg[binary]` — Alembic only; production migrations executed automatically when `RUN_MIGRATIONS_ON_START=1` (`docker-compose.yml:46`, `backend/docker-entrypoint.sh`)
- `email-validator` — required by Pydantic `EmailStr`
- `python-multipart` — required by FastAPI form parsing
- `aiosqlite` (dev only) — fast in-memory DB for tests

## Configuration

**Files:**
- `backend/pyproject.toml` — Python deps, Ruff, pytest config
- `bots/pyproject.toml` — aiogram + `doings-backend` editable install
- `frontend/package.json` — npm deps and scripts (`dev`, `build`, `preview`, `lint`, `format`)
- `frontend/tsconfig.json` — strict TS, `@/*` path alias to `src/*`
- `frontend/vite.config.ts` — Vite plugin, alias, dev proxy
- `frontend/tailwind.config.ts` — design tokens (HSL CSS vars), content globs
- `frontend/postcss.config.js` — Tailwind + autoprefixer
- `frontend/nginx.conf` — SPA fallback (`try_files $uri /index.html`)
- `infra/nginx/nginx.conf` — edge reverse proxy
- `infra/postgres/init.sql` — `pgcrypto`, `citext` extensions
- `backend/alembic.ini` + `backend/alembic/env.py` — migrations
- `backend/docker-entrypoint.sh` — optional `alembic upgrade head` on boot
- `docker-compose.yml` — full local topology
- `Makefile` — `up`, `down`, `logs`, `build`, `migrate`, `seed`, `fmt`, `lint`, `test`, `backend-shell`, `bot-shell`, `psql`

**Environment File:**
- `.env` is present at repo root (contents not read here); loaded by every service via `env_file: .env` in `docker-compose.yml`
- `backend/app/core/config.py` reads `.env` via Pydantic `SettingsConfigDict(env_file=".env")`
- `.env.example` is **not** present in the repo

**Env-var surface area** (defined in `backend/app/core/config.py:15-40` and `docker-compose.yml`):

| Variable | Default | Used by | Purpose |
|----------|---------|---------|---------|
| `POSTGRES_USER` | `doings` | postgres service | DB user |
| `POSTGRES_PASSWORD` | `doings` | postgres service | DB password |
| `POSTGRES_DB` | `doings` | postgres service | DB name |
| `DATABASE_URL` | `postgresql+asyncpg://doings:doings@postgres:5432/doings` | backend, bots | Async DSN |
| `DATABASE_URL_SYNC` | `postgresql+psycopg://doings:doings@postgres:5432/doings` | Alembic | Sync DSN for migrations |
| `REDIS_URL` | `redis://redis:6379/0` | backend, bots | Pub/sub + state |
| `JWT_SECRET` | `change-me` (must override) | backend | HS256 signing key |
| `JWT_ALG` | `HS256` | backend | JWT algorithm |
| `ACCESS_TOKEN_TTL_MINUTES` | `30` | backend | Access token lifetime |
| `REFRESH_TOKEN_TTL_DAYS` | `14` | backend | Refresh token lifetime |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost` | backend | Comma-separated allow-list |
| `TG_DOERS_BOT_TOKEN` | empty | bots, backend (initData verify) | DoersBot token from @BotFather |
| `TG_CUSTOMERS_BOT_TOKEN` | empty | bots, backend | CustomersBot token |
| `TG_REFEREE_BOT_TOKEN` | empty | bots, backend | RefereeBot token |
| `TG_WEBAPP_URL` | `http://localhost` | bots | Public URL exposed in Mini App buttons |
| `RATE_LIMIT_DEFAULT` | `120/minute` | backend | slowapi default limit |
| `APP_ENV` | `dev` | backend | Environment marker |
| `RUN_MIGRATIONS_ON_START` | `1` (set in compose) | backend entrypoint | Run `alembic upgrade head` on boot |
| `VITE_API_BASE_URL` | `/api/v1` | frontend build/runtime | Base path for API calls |

## Platform Requirements

**Development:**
- Docker + Docker Compose v2 (all services orchestrated via `docker compose up -d --build`)
- GNU Make (Makefile targets wrap all common workflows)
- Node 20 only required if running `npm` outside Docker (e.g. for `npm run lint`/`npm run format`)
- Python 3.12 only required for editor support; runtime is always containerized

**Production:**
- Container runtime (Docker / OCI) — the same `docker-compose.yml` is the deployment unit for the MVP
- Single-host topology: 1 nginx + 1 backend + 3 bots + 1 frontend + 1 Postgres + 1 Redis
- Ports exposed on host: `80` (nginx edge), `8000` (backend, for direct access), `5432` (Postgres), `6379` (Redis)
- Stateless API (JWT) — horizontal scaling possible behind nginx once slowapi is moved to a Redis backend (noted in `README.md`)

---

*Stack analysis: 2026-05-25*
