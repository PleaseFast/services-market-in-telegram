# Doings — Telegram-Native IT Freelance Marketplace

MVP platform where IT customers post projects and specialists apply, with deep Telegram integration via three bots:

- **DoingsForDoersBot** — specialist assistant + Mini App entry
- **DoingsForCustomersBot** — customer assistant + Mini App entry
- **RefereeBot** — anonymous customer↔specialist relay for early conversations

## Stack

| Layer        | Tech |
| ------------ | ---- |
| Frontend     | React 18, TypeScript, Vite, Tailwind, shadcn/ui, React Router, TanStack Query, Zustand, React Hook Form, Zod |
| Backend      | FastAPI, Python 3.12, SQLAlchemy 2 (async), Pydantic v2, Alembic, JWT, slowapi |
| Bots         | aiogram 3 (one process per bot, shared `app` package) |
| Data         | PostgreSQL 16, Redis 7 |
| Infra        | Docker Compose, Nginx |

## Architecture

```
React SPA / Telegram Mini App ──HTTP──▶ FastAPI ──┐
                                                  ├──▶ PostgreSQL
aiogram bots (3 procs) ───────────────────────────┘     Redis (pub/sub for notifications)
```

Business logic lives in `backend/app/services/` and is reused by both the REST API and the bot handlers — there is exactly one place a project's lifecycle is defined.

## Folder layout

```
backend/    FastAPI app, models, services, alembic, tests, seed
bots/       aiogram bots: common/, doers_bot/, customers_bot/, referee_bot/
frontend/   Vite + React + TS + Tailwind + shadcn/ui
infra/      nginx config, postgres init
```

## Quickstart

```bash
cp .env.example .env
# (optional) fill in TG_*_BOT_TOKEN values from @BotFather

make up           # builds and starts everything
make migrate      # runs alembic to head
make seed         # demo users, project templates
```

Then:

- App:        http://localhost
- API docs:   http://localhost/docs
- Postgres:   localhost:5432 (user/pass `doings`)

Useful commands:

```bash
make logs
make test         # pytest in backend container
make psql
make down
```

## Demo accounts (after `make seed`)

| Role       | Email                  | Password   |
| ---------- | ---------------------- | ---------- |
| Customer   | customer@demo.local    | demo1234!  |
| Specialist | specialist@demo.local  | demo1234!  |

## Domain model — ERD (textual)

```
users 1───1 specialist_profiles
users 1───1 customer_profiles
users 1───1 telegram_accounts
users 1───* projects (as customer_id)
users 1───* applications (as specialist_id)
projects 1───* applications
projects 1───* direct_offers
projects 1───* chat_threads
chat_threads 1───* messages
projects 1───* reviews
users 1───* notifications
```

## MVP roadmap

1. Auth (Telegram + email/password), profiles
2. Project create/publish, application & selection flow
3. Reviews + rating aggregation
4. RefereeBot anon chat + selection
5. Doers/Customers bots: notifications + Mini App entry
6. (next) File uploads (avatars) — currently URL only
7. (next) Search & filters (full-text on projects)
8. (next) Email transactional notifications
9. (next) Payments / escrow

## Future scaling

- Split bots and API onto separate compute; today they share images but are independent processes.
- Move notification fan-out from `asyncio.create_task` + Redis pub/sub to Celery/RQ with a persistent broker once volume warrants.
- Promote local volume avatars to S3-compatible object storage; the `files` service module is intentionally thin so the swap is one adapter.
- Read replica for `projects` feed; the public feed query is the hot path.
- Horizontal API behind nginx; sessions are stateless (JWT) and rate limiting can move to Redis-backed slowapi.
- For chat at scale, consider event sourcing on `messages` and a dedicated WebSocket gateway alongside the bot relay.

## License

Proprietary — internal MVP.
