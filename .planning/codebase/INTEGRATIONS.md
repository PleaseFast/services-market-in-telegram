# External Integrations

**Analysis Date:** 2026-05-25

> **Scope note:** This MVP has **no third-party SaaS integrations** beyond the Telegram Bot API. Everything else (DB, cache, reverse proxy) is self-hosted in `docker-compose.yml`. There is no email provider, no payment gateway, no object storage, no error-tracking SaaS, and no analytics service wired in.

## APIs & External Services

**Telegram (only external surface):**

- **Telegram Bot API** — long-polling consumed by three independent aiogram processes:
  - DoersBot — specialist assistant (`bots/doers_bot/main.py`); SDK: `aiogram>=3.10`; token env var: `TG_DOERS_BOT_TOKEN`
  - CustomersBot — customer assistant (`bots/customers_bot/main.py`); token: `TG_CUSTOMERS_BOT_TOKEN`
  - RefereeBot — anonymous customer↔specialist chat relay (`bots/referee_bot/main.py`); token: `TG_REFEREE_BOT_TOKEN`
  - Polling started via `Dispatcher.start_polling(bot, allowed_updates=dp.resolve_used_update_types())` in each bot's `main()` (e.g. `bots/doers_bot/main.py:93`)
  - All three are scheduled by the `x-bot-base` YAML anchor in `docker-compose.yml:3-15` (shared image + env_file)

- **Telegram Web App / Mini App SDK** — loaded directly from CDN in the SPA shell:
  - `<script src="https://telegram.org/js/telegram-web-app.js">` (`frontend/index.html:8`)
  - Thin wrapper in `frontend/src/lib/telegram.ts` exposes `getInitData()`, `isMiniApp()`, `applyTelegramTheme()`
  - The Mini App is launched from bot menus via `WebAppInfo(url=f"{settings.TG_WEBAPP_URL}/?role=...")` (e.g. `bots/doers_bot/main.py:33`)
  - The query-string role (`?role=specialist` / `?role=customer`) tells the SPA which side of the marketplace it's on

- **Telegram initData verification (server-side):**
  - HMAC-SHA256 check implemented from scratch in `backend/app/core/security.py:60` (`verify_telegram_init_data`)
  - Per-bot secret derived as `HMAC(b"WebAppData", bot_token, sha256)`; signed payload is sorted key=value joined by `\n`
  - `max_age_seconds=86400` enforced via `auth_date`
  - Consumed by the `POST /api/v1/auth/telegram` endpoint (`backend/app/api/v1/auth.py:25`) which accepts `{init_data, bot, role}` and returns a `TokenPair`

## Data Storage

**Primary Database:**
- **PostgreSQL 16** (image `postgres:16-alpine`) — `docker-compose.yml:18-33`
  - Connection (backend, async): `DATABASE_URL` → `postgresql+asyncpg://doings:doings@postgres:5432/doings`
  - Connection (Alembic, sync): `DATABASE_URL_SYNC` → `postgresql+psycopg://doings:doings@postgres:5432/doings`
  - Client: SQLAlchemy 2.0 async via `create_async_engine` in `backend/app/core/db.py:13`; sessions via `async_sessionmaker`
  - Initial extensions installed by `infra/postgres/init.sql`: `pgcrypto` (UUID/crypto), `citext` (case-insensitive email column)
  - Migrations: Alembic, versions in `backend/alembic/versions/`; bootstrap migration `20260525_0001_initial.py`
  - Auto-migrate on backend boot when `RUN_MIGRATIONS_ON_START=1` (set in `docker-compose.yml:46`) via `backend/docker-entrypoint.sh`
  - Healthcheck: `pg_isready -U $POSTGRES_USER` every 3s with 20 retries
  - Persisted via named volume `pg-data`

**Cache / Pub-Sub:**
- **Redis 7** (image `redis:7-alpine`) — `docker-compose.yml:35-38`
  - Connection: `REDIS_URL` → `redis://redis:6379/0`
  - Client: `redis.asyncio.Redis.from_url(..., decode_responses=True)` singleton in `backend/app/core/redis.py:8`
  - **Usage pattern: notification fan-out only.** Backend `publish`es JSON payloads on per-user channels (`notify:<user_id>` via `notify_channel()` in `backend/app/core/redis.py:15`); bots `psubscribe("notify:*")` and route to Telegram chats (`bots/common/notifications.py:31`)
  - Not used for caching, sessions, queues, or rate limiting in the MVP. The README explicitly notes future work to move slowapi onto Redis.
  - No persistence configured (no volume) — pub/sub is the only consumer so loss on restart is acceptable

**File Storage:**
- **None** — the MVP stores avatar/file references as URLs only. README §"Future scaling" notes intent to add S3-compatible object storage via a thin adapter in `app/services/files`.

**Search:**
- **None** — projects feed is plain Postgres queries. Full-text search is on the roadmap.

## Authentication & Identity

**Two auth paths, both producing the same JWT token pair:**

1. **Email + password** (`POST /api/v1/auth/register`, `POST /api/v1/auth/login`)
   - Passwords hashed with bcrypt via `passlib.CryptContext(schemes=["bcrypt"])` (`backend/app/core/security.py:16`)
   - Implementation: `app/services/auth.py` (`register_email`, `login_email`)

2. **Telegram Mini App initData** (`POST /api/v1/auth/telegram`)
   - Body specifies which bot's token to verify against (`bot: "doers" | "customers" | "referee"`)
   - Server resolves the token via `settings.all_bot_tokens` dict in `backend/app/core/config.py:47`
   - On success, looks up or creates the `User` + `TelegramAccount` link

**Tokens:**
- Access token: HS256 JWT, default TTL 30 min (`ACCESS_TOKEN_TTL_MINUTES`)
- Refresh token: HS256 JWT, default TTL 14 days (`REFRESH_TOKEN_TTL_DAYS`)
- Issued by `create_access_token` / `create_refresh_token` in `backend/app/core/security.py:40-51`
- Each token has a `jti` (random hex 8 bytes); refresh-token revocation is handled in `app/services/auth.py` (logout endpoint deletes the session row)
- Frontend stores tokens in Zustand (`frontend/src/stores/auth.ts`) and auto-refreshes on 401 inside `frontend/src/lib/api.ts:11`

**Authorization:**
- Role enum on `User` (`customer | specialist`), surfaced as `role` claim in the access token
- `CurrentUser` dependency wired in `backend/app/core/deps.py`; reused by every protected route

## Monitoring & Observability

**Error Tracking:**
- None. No Sentry, Rollbar, or equivalent SDK is in the dependency list.

**Logging:**
- stdlib `logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")`
- Configured at process start in `backend/app/main.py:16` and each bot's `main()`
- Captured by Docker (`make logs` runs `docker compose logs -f --tail=200`)

**Metrics / Tracing:**
- None.

**Healthcheck:**
- `GET /health` on the backend returns `{"status": "ok"}` (`backend/app/main.py:44`)
- Postgres healthcheck wired in `docker-compose.yml:29` and gates `backend` + bots via `depends_on.condition: service_healthy`

## CI/CD & Deployment

**Hosting:**
- Self-hosted via Docker Compose. The `docker-compose.yml` is the production unit.

**CI Pipeline:**
- None present in the repo (no `.github/`, no `.gitlab-ci.yml`, no `circleci`).
- Local CI surrogate via `make lint` (Ruff + ESLint) and `make test` (pytest in backend container).

**Reverse Proxy / Edge:**
- **Nginx 1.27 alpine** (`infra/nginx/nginx.conf`) routes the entire surface:
  - `/api/` → `backend:8000` (preserves `Host`, sets `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`; 60s read timeout)
  - `/docs`, `/redoc`, `/openapi.json` → `backend:8000` (FastAPI's OpenAPI surface, exposed publicly in MVP)
  - `/` → `frontend:80` (SPA served by an inner nginx with `try_files $uri /index.html`)
  - Body limit: `client_max_body_size 10m`
  - `server_tokens off`
- Backend port 8000 is **also** published to the host for direct access (`docker-compose.yml:53`)

## OpenAPI Surface

- Spec auto-generated by FastAPI; served at `/openapi.json`
- Interactive docs at `/docs` (Swagger UI) and `/redoc`
- All routes mounted under the `/api/v1` prefix in `backend/app/api/router.py:14`:
  - `auth.router` — register/login/telegram/refresh/logout/me (`backend/app/api/v1/auth.py`)
  - `users.router`
  - `specialists.router`
  - `customers.router`
  - `projects.router`
  - `applications.router`
  - `reviews.router`
  - `notifications.router`
- CORS allow-list: `CORS_ORIGINS` env var, comma-separated (defaults `http://localhost:5173,http://localhost`); credentials allowed; all methods/headers (`backend/app/main.py:32`)
- Rate limiting: slowapi `Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])` — in-process counters keyed by `X-Forwarded-For`-resolved remote address (`backend/app/main.py:19`)

## Mini App Boundary

- **Client side:** Vite SPA loads `telegram-web-app.js` from Telegram's CDN; checks `window.Telegram.WebApp.initData` at boot (`frontend/src/lib/telegram.ts:5`). When present, `isMiniApp()` returns true and the SPA exchanges `initData` for a JWT pair via `POST /auth/telegram`.
- **Server side:** `verify_telegram_init_data(init_data, bot_token)` (`backend/app/core/security.py:60`) is the only trust boundary — it computes the HMAC and rejects expired (`auth_date > 24h`) or tampered payloads.
- **Bot side:** Each bot's `/start` handler links the Telegram user id to the existing app user via `update_chat_id(session, message.from_user.id, message.chat.id)` (`bots/common/auth.py:21`). DoersBot and CustomersBot expose the Mini App as an inline `WebAppInfo` button using `TG_WEBAPP_URL`.
- **Identity bridge:** `telegram_accounts` table (`app/models/telegram.py`) links one `User` ↔ one `tg_user_id`, plus a cached `chat_id` so notification fan-out can DM the right Telegram chat without re-asking Telegram.

## Webhooks & Callbacks

**Incoming:**
- None. All bot updates come via long-polling (`Dispatcher.start_polling`). There is no webhook endpoint mounted on the FastAPI app for Telegram.

**Outgoing:**
- The backend never calls Telegram directly. All outbound Telegram messages flow:
  1. Service layer publishes JSON to Redis channel `notify:<user_id>` (`backend/app/services/notifications.py`)
  2. The appropriate bot process (subscribed via `psubscribe("notify:*")` in `bots/common/notifications.py:31`) calls `bot.send_message(chat_id, text)`
- The RefereeBot additionally forwards chat messages synchronously inside its own handler (`bots/referee_bot/main.py:259`), looking up the counterparty's `chat_id` from `telegram_accounts`.

## Environment Configuration

**Required env vars (for a functional deployment):**
- `JWT_SECRET` — must be overridden from the `change-me` default
- `TG_DOERS_BOT_TOKEN`, `TG_CUSTOMERS_BOT_TOKEN`, `TG_REFEREE_BOT_TOKEN` — empty defaults; bots refuse to start without their own token (`bots/doers_bot/main.py:80`, `bots/referee_bot/main.py:297`)
- `TG_WEBAPP_URL` — public URL where the Mini App is reachable; embedded in inline keyboard buttons
- `CORS_ORIGINS` — must include the Mini App origin (Telegram serves it from the configured `TG_WEBAPP_URL`)

**Optional / has working default:**
- `DATABASE_URL`, `DATABASE_URL_SYNC`, `REDIS_URL`, `POSTGRES_*` — sensible compose-network defaults
- `ACCESS_TOKEN_TTL_MINUTES`, `REFRESH_TOKEN_TTL_DAYS`, `RATE_LIMIT_DEFAULT`, `APP_ENV`
- `VITE_API_BASE_URL` — defaults to `/api/v1` (set in `frontend/Dockerfile:3` and re-asserted via the `frontend` service env in `docker-compose.yml:73`)

**Secrets location:**
- `.env` at repo root, gitignored (`.gitignore:18`). Loaded by Compose via `env_file: .env` on every service. No external secret manager (Vault / SOPS / cloud KMS) is integrated.
- `.env.example` is **not** present — operators must read `backend/app/core/config.py` to discover the variable surface.

---

*Integration audit: 2026-05-25*
