# Frontend — React + Vite + Tailwind + shadcn/ui

## Layout

```
src/
├── app/                 router, App shell, providers
├── components/ui/       shadcn-style primitives (button, input, card, …)
├── features/
│   ├── auth/            login / register pages + API
│   ├── landing/         marketing + 404
│   ├── projects/        types + TanStack Query hooks for projects/apps
│   ├── specialist/      specialist dashboard, feed, profile, archive
│   ├── customer/        dashboard, create, projects, applicants, catalog
│   └── notifications/   shared notifications page
├── lib/                 api client, telegram helpers, utils
├── stores/              zustand (auth)
└── styles.css           Tailwind + shadcn CSS variables
```

## Dev

```bash
npm install
npm run dev
# Vite proxies /api/* to http://localhost:8000
```

Set `VITE_API_BASE_URL` to point at a custom backend URL (defaults to
`/api/v1`, which works behind nginx in compose).

## Telegram Mini App

The page includes `telegram-web-app.js`. On boot, `App.tsx` checks for
`window.Telegram.WebApp.initData`; if present, it posts to `/auth/telegram`
and stores the resulting tokens — the same SPA seamlessly serves both
browser visitors and Mini App users.

The bots' inline keyboards open URLs like
`${TG_WEBAPP_URL}/?role=specialist` so the first visit lands on the right
surface.

## Adding more shadcn components

Components in `components/ui/*` are inlined (not pulled via the shadcn CLI)
to keep this MVP container-buildable without network access. Add more
following the same pattern.
