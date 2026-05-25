# Coding Conventions

**Analysis Date:** 2026-05-25

## Naming Patterns

**Files (Python):**
- Lowercase, snake_case modules: `backend/app/services/projects.py`, `backend/app/repositories/projects.py`
- Test modules prefixed with `test_`: `backend/tests/test_project_flow.py`
- One concept per module, grouped by layer (`services/`, `repositories/`, `schemas/`, `models/`, `api/`)

**Files (TypeScript/React):**
- React components and pages: `PascalCase.tsx` (e.g. `frontend/src/features/auth/pages/RegisterPage.tsx`)
- UI primitives: `lowercase.tsx` (e.g. `frontend/src/components/ui/button.tsx`)
- Utilities and stores: `lowercase.ts` (e.g. `frontend/src/lib/api.ts`, `frontend/src/stores/auth.ts`)

**Functions:**
- Python: `snake_case`, async functions prefixed with verb (`create_project`, `select_specialist`, `_owned_project` for private helpers)
- TypeScript: `camelCase` (`refreshAccess`, `onSubmit`), React components `PascalCase` (`RegisterPage`, `Button`)
- Private/internal Python helpers use leading underscore: `_ensure_customer`, `_owned_project`

**Variables:**
- Python: `snake_case`
- TypeScript: `camelCase`, constants `UPPER_SNAKE_CASE` (`BASE_URL` in `frontend/src/lib/api.ts`)

**Types/Classes:**
- Python: `PascalCase` (`DomainError`, `ProjectStatus`, `Application`)
- TypeScript: `PascalCase` types, interfaces, and React components (`ButtonProps`, `FormValues`, `ApiError`)
- Enums: Python uses uppercase members (`UserRole.CUSTOMER`, `ProjectStatus.OPEN`)

## Code Style

**Formatting (Python):**
- Tool: `ruff` (configured in `backend/pyproject.toml`)
- Line length: 100
- Target: `py312`
- `from __future__ import annotations` used at top of modules for forward-reference friendliness

**Linting (Python):**
- Tool: `ruff` (`backend/pyproject.toml` → `[tool.ruff.lint]`)
- Selected rule groups: `E`, `F`, `I` (isort), `B` (bugbear), `UP` (pyupgrade), `W`
- Ignored: `B008` — allowed for FastAPI `Depends(...)` defaults

**Formatting/Linting (TypeScript):**
- TypeScript `strict: true` (`frontend/tsconfig.json`)
- `noFallthroughCasesInSwitch: true`
- `noUnusedLocals` / `noUnusedParameters` intentionally `false` to allow scaffolding-friendly DX
- No Prettier/ESLint config detected — rely on TS strict + editor defaults

## Import Organization

**Python order (enforced by ruff `I`):**
1. `from __future__ import annotations`
2. Standard library
3. Third-party (`fastapi`, `sqlalchemy`, `pydantic`)
4. First-party (`app.*`)

Example (`backend/app/services/projects.py`):
```python
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus
from app.services.errors import ConflictError, ForbiddenError, NotFoundError
```

**TypeScript order:**
1. Third-party (`react`, `react-hook-form`, `zod`, `@radix-ui/*`, `class-variance-authority`)
2. Path-aliased first-party (`@/components/...`, `@/lib/...`, `@/stores/...`)
3. Relative imports (`../api`)

**Path Aliases:**
- `@/* -> src/*` (`frontend/tsconfig.json`)
- Always prefer `@/...` over deep relatives for cross-feature imports

## Error Handling

**Backend pattern — domain exceptions:**
- Service layer raises `DomainError` subclasses from `backend/app/services/errors.py`:
  - `NotFoundError` → 404
  - `ConflictError` → 409
  - `ForbiddenError` → 403
  - Base `DomainError(message, status_code=400)` for other cases
- A FastAPI exception handler in `backend/app/main.py` translates them to HTTP responses
- API/route code does NOT raise `HTTPException` directly — it calls a service and lets the handler translate

Example (`backend/app/services/projects.py`):
```python
def _ensure_customer(user: User) -> None:
    if user.role != UserRole.CUSTOMER:
        raise ForbiddenError("Only customers can perform this action")
```

**Frontend pattern — `ApiError`:**
- All HTTP errors flow through `ApiError` in `frontend/src/lib/api.ts`
- Carries `status: number` and `detail: string` (parsed from server's `detail` field)
- Pages catch unknown, surface `.message` inline (no global toast required)

```ts
} catch (e: unknown) {
  setErr((e as Error).message);
}
```

## Logging

**Backend:** No app-level logger pattern enforced; FastAPI/uvicorn defaults handle request logging.

**Frontend:** No logging library. Errors surface in-UI via state + destructive-toned text.

## Comments

**When to comment:**
- Section dividers in service modules: `# --- helpers ---` (`backend/app/services/projects.py:154`)
- Inline explanations for non-obvious business rules
- Module-level docstrings on shared abstractions (e.g. `DomainError` class docstring)

**No JSDoc/TSDoc convention** observed in frontend; rely on TS types for self-documentation.

## Function Design

**Backend services:**
- Async-first: every service function is `async def`
- First arg is always `session: AsyncSession`, then `user: User`, then domain inputs
- Return the domain model (e.g. `Project`), not a serialized dict — schemas convert at the API boundary
- Private helpers (leading `_`) at module bottom under a `# --- helpers ---` divider

**Backend repositories vs services:**
- Repositories under `backend/app/repositories/` are **pure data access** (e.g. `get_project`) — they do NOT enforce auth or business rules
- Services compose repository calls and enforce ownership, status transitions, and side effects (notifications, related-row mutations)

**Frontend handlers:**
- `onSubmit(values)` defined inside the component, awaits API, navigates or sets error state
- Use `react-hook-form` `formState.isSubmitting` to disable submit buttons

## Module Design

**Backend:**
- One responsibility per module; group by layer
- Layered imports flow strictly: `api -> services -> repositories -> models`
- `from app.models import Base` for Alembic/test schema bootstrapping

**Frontend:**
- Feature-first under `frontend/src/features/<feature>/{pages,api,components}`
- Shared UI primitives under `frontend/src/components/ui/` (shadcn-style)
- Co-locate Zod schemas with the form/page that uses them (see `RegisterPage.tsx`)
- No barrel `index.ts` re-exports — import the file directly

## ORM / Schema Conventions

**SQLAlchemy 2.0 typed models:**
- Use `Mapped[...]` annotations + `mapped_column(...)`
- Models in `backend/app/models/` inherit from a shared `Base`
- Enums stored as Python `enum.Enum` (e.g. `ProjectStatus`, `UserRole`, `ApplicationStatus`)
- Soft-delete via `deleted_at` column (checked in `_owned_project` / `_project_visible_to`)

**Pydantic v2 schemas:**
- Schemas in `backend/app/schemas/` (e.g. `ProjectIn`, `ProjectPatch`)
- Shared base `ORMBase` sets `model_config = ConfigDict(from_attributes=True)` to enable ORM → schema conversion
- Use `patch.model_dump(exclude_unset=True)` for PATCH semantics (only assign provided fields)

## FastAPI Dependencies

Defined in `backend/app/core/deps.py`:
- `SessionDep` — provides `AsyncSession`
- `CurrentUser` — authenticated user
- `CustomerOnly` / `SpecialistOnly` — role-gated current user

Usage: declare as default args on route handlers; ruff's `B008` is intentionally ignored for this idiom.

## Frontend State Management

**Server state:** TanStack Query (no global cache hand-rolling).

**Client/auth state:** Zustand store at `frontend/src/stores/auth.ts`, persisted (tokens survive reload). Access via `useAuthStore.getState()` outside React (see `frontend/src/lib/api.ts`) or `useAuthStore(selector)` inside components.

**Forms:** React Hook Form + `@hookform/resolvers/zod` with a colocated Zod `schema` and inferred `FormValues` type.

```ts
const schema = z.object({ email: z.string().email(), password: z.string().min(8) });
type FormValues = z.infer<typeof schema>;
useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: {...} });
```

## UI Primitives (shadcn-style)

Located in `frontend/src/components/ui/` (e.g. `button.tsx`, `card.tsx`, `input.tsx`, `label.tsx`).

**Variant pattern:** `class-variance-authority` (`cva`) defines a base class string plus `variants` and `defaultVariants`. Components expose `VariantProps<typeof xxxVariants>` on their props.

**Class merging:** `cn` helper from `@/lib/utils` (clsx + tailwind-merge) — always wrap composed classNames.

**Polymorphism:** `asChild` + `@radix-ui/react-slot` lets primitives render as their child (see `Button`).

**Forward refs:** UI primitives use `React.forwardRef` and set `.displayName`.

## Styling

**Tailwind:** Dark-mode via `class` strategy. Design tokens defined as CSS variables in `frontend/src/styles.css` (consumed via `bg-primary`, `text-destructive`, etc.).

**Error text:** Inline `<p className="text-xs text-destructive">{errors.field.message}</p>` (see `RegisterPage.tsx`).

**Layout:** Utility-first; cards/sections composed from `Card`, `CardHeader`, `CardContent`, `CardTitle` primitives.

## HTTP Client Convention

`frontend/src/lib/api.ts` exports:
- `api<T>(path, init)` — base fetch wrapper, auto-attaches `Authorization: Bearer <accessToken>`, transparently refreshes on 401 via `/auth/refresh`, throws `ApiError` on non-2xx
- `http.{get,post,put,patch,del}` — verb shortcuts that JSON-encode bodies

Feature `api.ts` modules call `http.*` and return typed payloads; pages call those, never `fetch` directly.

---

*Convention analysis: 2026-05-25*
