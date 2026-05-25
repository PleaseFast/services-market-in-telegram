# Codebase Concerns

**Analysis Date:** 2026-05-25

## Tech Debt

**Test/Prod database divergence (HIGH):**
- Issue: Tests run against SQLite while production targets Postgres. SQLAlchemy models are dialect-portable, but PG-specific behavior (CITEXT case-insensitive uniqueness, JSONB query operators, `gen_random_uuid()`, enum semantics) is never exercised in CI.
- Files: `backend/alembic/versions/20260525_0001_initial.py`, `backend/tests/conftest.py` (SQLite fixture), `backend/app/models/*.py`
- Impact: Bugs caught only in staging/prod; enum coercion, JSONB containment queries, and unique constraints on case-folded text may behave differently than tested.
- Fix approach: Add a `pytest` marker `@pytest.mark.pg` that runs a subset of tests against a real Postgres (testcontainers or service container in CI); require it for any migration or model touching JSONB/CITEXT/enums.

**RefereeBot drops non-text messages silently (MEDIUM):**
- Issue: The in-thread handler is registered with `F.text & ~F.text.startswith("/")` only — photos, voice, documents, stickers, video notes, and locations hit no handler and are silently ignored without user feedback.
- Files: `bots/referee_bot/main.py:314` (handler registration), `bots/referee_bot/main.py:259-292` (`on_text_in_thread`)
- Impact: Customers/specialists sending attachments believe the message went through; anonymity-preserving chat fails for any media exchange (which is common for portfolios, screenshots, voice briefs).
- Fix approach: Register a catch-all handler for `ChatState.in_thread` that either (a) replies "only text is supported, attachments are not relayed" or (b) extends `post_message` to persist + relay media via `bot.copy_message` while preserving anonymity by stripping captions referring to the sender.

**Soft-delete leaves profile rows orphaned (MEDIUM):**
- Issue: `delete_user` only flips `is_active`/`deleted_at` and nulls `email`, but leaves `specialist_profile`/`customer_profile` and `telegram_account` rows intact and joined to the soft-deleted `user_id`. Telegram ID stays tied to the dead account, preventing the same TG user from re-signing up cleanly.
- Files: `backend/app/services/profiles.py:73-80`
- Impact: Re-registration via Telegram for the same `tg_user_id` resolves to the deleted user (see `login_telegram` → `get_user_by_tg_id` at `backend/app/services/auth.py:81`), so a "deleted" account effectively cannot be recreated.
- Fix approach: In `delete_user`, also null/scrub PII on profile rows (or cascade-delete them) and detach `TelegramAccount` rows (delete or null `tg_user_id` if model allows). Add a migration if the column is `NOT NULL`.

**`bcrypt` 72-byte truncation not enforced (MEDIUM):**
- Issue: `RegisterIn` (Pydantic) accepts passwords up to 128 chars, but `passlib`/`bcrypt` silently truncates anything beyond 72 bytes. A user with a 100-char passphrase actually authenticates on the first 72 bytes.
- Files: `backend/app/schemas/auth.py` (`RegisterIn.password` `max_length=128`), `backend/app/core/security.py` (`hash_password`/`verify_password`), `backend/app/services/auth.py:42-52`
- Impact: Confusing for security-conscious users; password-rotation tooling that picks the last N chars of a long input may produce identical hashes — false uniqueness.
- Fix approach: Enforce `max_length=72` on `RegisterIn.password` *or* pre-hash with SHA-256 before bcrypt (and add a migration plan for existing hashes). The simplest fix is the schema cap.

**Frontend has zero test coverage (HIGH):**
- Issue: No `*.test.*` / `*.spec.*` files anywhere under `frontend/src`. No `vitest`/`jest`/`playwright` configured.
- Files: `frontend/` (entire tree)
- Impact: Refactors of `useAuthStore`, route guards, role-switch flows, and Mini App initData handshakes have no safety net. Regressions reach prod.
- Fix approach: Add `vitest` + `@testing-library/react` for unit/component tests; start with `stores/auth.ts`, the API client, and route guards. Add Playwright for the login/role-pick happy path.

**Refresh tokens never garbage-collected (MEDIUM):**
- Issue: `_issue_tokens` inserts a `RefreshToken` row on every login/refresh. `refresh_session` only marks rows `revoked_at`. No periodic job deletes expired/revoked rows.
- Files: `backend/app/services/auth.py:27-39, 128-150`, `backend/app/models/user.py` (`RefreshToken`)
- Impact: `refresh_tokens` grows unbounded; query plans on `WHERE jti = ?` stay fine due to the unique index, but storage and backup size balloon over time.
- Fix approach: Add a periodic cleanup (Alembic-scheduled cron or a worker task) deleting rows where `revoked_at IS NOT NULL OR expires_at < now() - interval '7 days'`. Index on `expires_at` for the sweep.

**`slowapi` rate limiter is in-process (MEDIUM):**
- Issue: Default `slowapi` uses an in-memory `Limiter` keyed per worker. Behind horizontal scale (>1 uvicorn worker / >1 pod) limits are effectively multiplied by the worker count.
- Files: `backend/app/main.py` (limiter setup), `backend/app/api/routers/*` (decorators)
- Impact: Brute-force protection on `/auth/login` and other limited endpoints weakens linearly with scale-out.
- Fix approach: Configure `slowapi` with a Redis storage backend (`limits.storage.RedisStorage`) using the existing `REDIS_URL`. Keyed by IP and/or user ID.

**JWT in `localStorage` via persisted Zustand store (HIGH):**
- Issue: `useAuthStore` persists `accessToken` and `refreshToken` to `localStorage` under key `doings-auth`. Any XSS (including from a vulnerable dependency or a future user-content rendering bug) exfiltrates both tokens.
- Files: `frontend/src/stores/auth.ts:21-33`
- Impact: Compromised tokens grant full session access including refresh — attacker keeps rolling forever.
- Fix approach: Move `refreshToken` to an httpOnly, SameSite=Strict cookie issued by the backend; keep `accessToken` in memory only (lose-on-reload, refresh from cookie). Add CSRF token for cookie-backed mutating requests, or rely on SameSite + custom header.

**No CSRF protection (MEDIUM):**
- Issue: Tied to the previous item — current design uses `Authorization: Bearer` so CSRF is moot. The moment auth moves to cookies (recommended above), CSRF mitigation becomes mandatory.
- Files: `backend/app/main.py`, `frontend/src/api/client.ts`
- Impact: Pre-emptive concern: do not migrate to cookie auth without adding CSRF tokens or strict SameSite + origin checks.
- Fix approach: Use `fastapi-csrf-protect` or implement a double-submit cookie pattern; pair with the auth-cookie migration above.

**No file upload pipeline (LOW):**
- Issue: `avatar_url` fields are arbitrary strings (`max_length=500`) and there is no `app/services/files.py` despite the README referencing it. Users pass any URL; no validation that it's an image, on a trusted host, or virus-scanned.
- Files: `backend/app/schemas/profile.py:41, 63`, `backend/app/services/` (no `files.py`), `README.md`
- Impact: SSRF risk if the backend ever fetches the URL; brand risk from hot-linked NSFW content; broken images.
- Fix approach: Add an S3/MinIO-backed upload endpoint that returns a signed URL; restrict `avatar_url` to that host via a Pydantic validator; render via `<img referrerpolicy="no-referrer">`.

**CORS default is dev-only (LOW):**
- Issue: `CORS_ORIGINS` defaults to `http://localhost:5173,http://localhost`. If env config is missing in a staging/prod deploy, the API silently rejects the real frontend.
- Files: `backend/app/core/config.py:28-29, 43-44`
- Impact: Deployment misconfigurations cause silent 4xx on every request. Conversely, if someone "fixes" it by adding `*`, that opens auth-token theft via cross-origin XHR.
- Fix approach: Fail-fast in `settings` validation when `ENV in {staging, prod}` and `CORS_ORIGINS` still equals the default; explicit allowlist required.

**No structured logging (LOW):**
- Issue: Bots and backend use `logging.basicConfig(level=INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")` — plain text only. No JSON, no request IDs, no correlation between web requests and bot DMs.
- Files: `bots/referee_bot/main.py:296`, `bots/common/notifications.py:14`, `backend/app/main.py` (logging setup)
- Impact: Production debugging of a chat-relay outage is painful — cannot correlate `notify:*` publish with the bot DM send.
- Fix approach: Adopt `structlog` (or `python-json-logger`) with a request-ID middleware on FastAPI and a context var propagated to bot handlers. Emit one line per stage with `event=`, `user_id=`, `correlation_id=`.

**Generous Telegram initData TTL (LOW):**
- Issue: `verify_telegram_init_data` accepts initData up to 24h old (`max_age_seconds=86400`). Telegram's own recommendation is much tighter (typically minutes).
- Files: `backend/app/core/security.py:60, 81`
- Impact: A leaked `tgWebAppData` query string remains valid for a day — replay risk if a user shares a Mini App link or it shows up in proxy logs.
- Fix approach: Default to 3600s (1h) or shorter; expose as a setting `TG_INITDATA_MAX_AGE_SECONDS` so dev can keep it generous.

**Alembic `script.py.mako` `Sequence` import note (LOW):**
- Issue: The autogenerate template imports `Sequence` from `typing` only when autogenerate fills it. Cosmetic; not a runtime issue.
- Files: `backend/alembic/script.py.mako`
- Impact: None today; documented for awareness so future contributors don't "clean up" the import and break autogenerate output.
- Fix approach: No action required. If editing the template, keep the conditional `Sequence` import.

**`selectinload` + `from __future__ import annotations` eager-defaults caveat (LOW):**
- Issue: `app/repositories/users.py` uses `selectinload(...)` against relationships defined on models that use `from __future__ import annotations`. Tests pass, but SQLAlchemy's relationship resolution from stringified annotations can need `eager_defaults` / explicit `Mapped[...]` types if model layout changes.
- Files: `backend/app/repositories/users.py`, `backend/app/models/user.py`, `backend/app/models/profile.py`
- Impact: Adding a new relationship without explicit `Mapped[...]` typing can produce mapper-init errors at import time.
- Fix approach: Keep all relationships explicitly typed `Mapped[list["X"]]` / `Mapped["X"]`; add a tiny test that imports every model module to fail fast on mapper init.

**Frontend Dockerfile builds without a lockfile (HIGH):**
- Issue: `frontend/Dockerfile:4` copies `package-lock.json*` (optional) and runs `npm install --legacy-peer-deps`. The repo has **no** `frontend/package-lock.json` committed (confirmed via `ls`), so every image build resolves dependencies fresh against the npm registry.
- Files: `frontend/Dockerfile:4-5`, `frontend/package.json`, missing `frontend/package-lock.json`
- Impact: Non-reproducible builds; CVE windows differ image-to-image; a malicious version bump in a transitive dep can ship to prod between deploys.
- Fix approach: Run `npm install` locally, commit `package-lock.json`, switch the Dockerfile to `npm ci --legacy-peer-deps`, and add a CI check that fails if the lockfile is missing or out of sync.

## Known Bugs

**Notifications dispatcher swallows all errors with no retry / DLQ (HIGH):**
- Symptoms: A transient Telegram 5xx, a bot-blocked-by-user, or any DB hiccup during `user_chat_lookup` is caught by the bare `except Exception:` and logged — the notification is lost forever. No retry, no dead-letter, no metric.
- Files: `bots/common/notifications.py:48-50`
- Trigger: Any DM failure during `bot.send_message`; pubsub message loss while a worker is restarting (pubsub is fire-and-forget — no replay).
- Workaround: None in code. Operationally: monitor `Failed to deliver notification` log lines.
- Fix approach: Replace Redis pubsub with Redis Streams (`XADD`/`XREADGROUP`) for at-least-once delivery; add exponential backoff per message; route after N retries to a `notify:dead` stream for manual replay.

## Security Considerations

See HIGH-severity items above: **JWT in localStorage** (`frontend/src/stores/auth.ts:21-33`), **CSRF gap if migrating to cookies**, **bcrypt truncation**, **generous initData TTL**, **CORS default**, and **non-reproducible frontend builds**. Together they form the bulk of the pre-prod security backlog.

## Performance Bottlenecks

**Unbounded `refresh_tokens` growth (MEDIUM):**
- Problem: See "Refresh tokens never garbage-collected" — table grows linearly with active users × refresh frequency, forever.
- Files: `backend/app/services/auth.py:31-37`
- Cause: No cleanup job.
- Improvement path: Sweep job as described above.

**`upsert_specialist_profile` rewrites all child rows (LOW):**
- Problem: Every profile save deletes all `workplaces`/`portfolio_links` and re-inserts them, even on a no-op edit.
- Files: `backend/app/services/profiles.py:43-51`
- Cause: "Rewrite for simplicity" comment at line 43.
- Improvement path: Diff incoming vs persisted lists; only insert/update/delete changed rows. Acceptable to defer until profile sizes grow.

## Fragile Areas

**RefereeBot FSM state vs. handler registration order (MEDIUM):**
- Files: `bots/referee_bot/main.py:303-314`
- Why fragile: The `on_text_in_thread` handler is registered last with both a state filter (`ChatState.in_thread`) and a content filter. Any future handler registered above it with a broader filter will steal the in-thread relay. There is no test for handler ordering.
- Safe modification: Add new handlers above only with explicit state filters; keep the in-thread handler the broadest text matcher.
- Test coverage: No tests for bot dispatch.

**`auth.py` mixed-mode user creation (LOW):**
- Files: `backend/app/services/auth.py:64-100`
- Why fragile: `login_telegram` creates a `User` row when none exists. Race-free under one worker but two near-simultaneous Mini App opens with the same `tg_user_id` could both reach `get_user_by_tg_id == None` and both insert (the unique constraint on `TelegramAccount.tg_user_id` will save the second one, but at the cost of a 500 response).
- Safe modification: Wrap the lookup+create in `INSERT ... ON CONFLICT DO NOTHING RETURNING` (Postgres) or catch `IntegrityError` and re-fetch.
- Test coverage: Happy path only; no concurrency test.

## Scaling Limits

**In-process rate limiter (MEDIUM):**
- Current capacity: 1 uvicorn worker. Limits are per-process.
- Limit: Any horizontal scale-out (gunicorn workers or pods) multiplies the allowed rate.
- Scaling path: Redis storage backend for `slowapi` (see Tech Debt).

**Redis pubsub fan-out for notifications (MEDIUM):**
- Current capacity: All subscribers must be online at publish time.
- Limit: Any restart, deploy, or transient disconnect drops in-flight notifications — they are not replayed.
- Scaling path: Migrate to Redis Streams with consumer groups (see "Notifications dispatcher" bug).

## Dependencies at Risk

**Frontend has no lockfile (HIGH):**
- Risk: Every install resolves transitive deps fresh.
- Impact: Non-reproducible builds; surprise upgrades; supply-chain blast radius.
- Migration plan: Commit `frontend/package-lock.json` and switch Docker to `npm ci`.

## Missing Critical Features

**File upload pipeline (LOW):**
- Problem: `app/services/files.py` is referenced in `README.md` but does not exist; avatars are URL-only.
- Blocks: Real avatar UX, attachment relay in RefereeBot, portfolio media for specialists.

**Structured logging + request correlation (LOW):**
- Problem: Plain-text logs across backend + 2 bots make cross-service debugging painful.
- Blocks: Production triage of any cross-service flow (e.g. "user clicked X in Mini App but bot never DM'd").

## Test Coverage Gaps

**Frontend (HIGH):**
- What's not tested: Everything — stores, route guards, API client, components, role-pick flow.
- Files: `frontend/src/**`
- Risk: Any refactor risks silent regressions in login/persistence/role-switch.
- Priority: High.

**Bots (HIGH):**
- What's not tested: `bots/referee_bot/main.py` handlers, `bots/common/notifications.py` loop, `bots/common/auth.py` linking.
- Files: `bots/**`
- Risk: Relay correctness, ordering, media-drop, notification delivery — all unverified.
- Priority: High.

**Postgres-specific behavior (HIGH):**
- What's not tested: JSONB containment queries, CITEXT case-insensitive email lookups, enum coercion, `gen_random_uuid()` defaults.
- Files: `backend/tests/conftest.py` (SQLite-only fixture)
- Risk: Production-only bugs.
- Priority: High.

**Concurrent first-time TG signup (LOW):**
- What's not tested: Two parallel `login_telegram` calls for the same `tg_user_id`.
- Files: `backend/app/services/auth.py:81-96`
- Risk: 500 on race; user sees retry-able error.
- Priority: Low.

---

*Concerns audit: 2026-05-25*
