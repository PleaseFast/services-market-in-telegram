"""Curated project templates surfaced to customers when creating a project.

Roughly 8-12 templates per category covering distinct niches and complexity
levels. The seed loader dedupes by ``title``, so adding new entries here and
re-running ``make seed`` will safely insert only the new ones.
"""

PROJECT_TEMPLATES: list[dict[str, str]] = [
    # ---------------- Frontend ----------------
    {
        "title": "Landing page for SaaS product",
        "category": "Frontend",
        "description_template": (
            "Build a responsive marketing landing page. Sections: hero, features, "
            "pricing, FAQ, footer. Stack open to suggestion (Next.js preferred). "
            "Deliverables: deployed preview, Lighthouse >= 90, CMS-friendly copy blocks."
        ),
    },
    {
        "title": "Marketing site rebuild in Next.js",
        "category": "Frontend",
        "description_template": (
            "Rebuild our 6-8 page marketing site in Next.js (App Router). Migrate copy "
            "and assets from the current WordPress site, integrate a headless CMS "
            "(Sanity or Contentful), keep SEO parity with existing URLs and meta."
        ),
    },
    {
        "title": "Admin panel with CRUD tables",
        "category": "Frontend",
        "description_template": (
            "Internal admin panel against our existing REST API. ~6 entities, each "
            "with list / detail / create / edit / delete, server-side pagination, "
            "filters, role-based access. React + shadcn/ui or Refine acceptable."
        ),
    },
    {
        "title": "Analytics dashboard from Figma",
        "category": "Frontend",
        "description_template": (
            "Implement a multi-tab analytics dashboard from finalized Figma designs. "
            "Charts via Recharts or Tremor, date-range filter, CSV export. Data comes "
            "from a documented JSON API. Pixel parity on desktop, responsive on tablet."
        ),
    },
    {
        "title": "Performance + SSR optimization",
        "category": "Frontend",
        "description_template": (
            "Our Next.js app scores 40-55 on Lighthouse mobile. Audit and fix: ship "
            "SSR/ISR where appropriate, eliminate render-blocking JS, optimize images "
            "and fonts, fix CLS. Target: 85+ on the 5 most trafficked pages."
        ),
    },
    {
        "title": "Framer Motion animations + microinteractions",
        "category": "Frontend",
        "description_template": (
            "Add polished motion across 8-10 surfaces (nav, modals, list reorder, "
            "page transitions, hero entrance). Use Framer Motion. Respect "
            "prefers-reduced-motion. Deliver a small reusable variants library."
        ),
    },
    {
        "title": "Design-system component library refactor",
        "category": "Frontend",
        "description_template": (
            "Consolidate scattered components into a shared library (Button, Input, "
            "Select, Modal, Toast, Table, etc.) with Storybook docs, TypeScript "
            "props, accessible primitives (Radix or Headless UI), and dark mode."
        ),
    },
    {
        "title": "Embeddable widget for third-party sites",
        "category": "Frontend",
        "description_template": (
            "Build a JS widget partners can drop into their site with one <script> "
            "tag. Isolated styles (Shadow DOM), configurable via data-attributes, "
            "loads async, < 30kb gzipped. Demo page + integration docs."
        ),
    },
    {
        "title": "Accessibility audit + WCAG fixes",
        "category": "Frontend",
        "description_template": (
            "Audit our app against WCAG 2.1 AA. Deliver a prioritized issues list "
            "(axe + manual screen-reader pass) and implement fixes: keyboard nav, "
            "focus management, ARIA, contrast, form labeling."
        ),
    },
    {
        "title": "A/B test instrumentation",
        "category": "Frontend",
        "description_template": (
            "Wire up GrowthBook (or LaunchDarkly / PostHog experiments) across "
            "checkout funnel and onboarding. Add 3 starter experiments, document "
            "the variant pattern, and integrate with our analytics events."
        ),
    },
    {
        "title": "Chrome extension MVP",
        "category": "Frontend",
        "description_template": (
            "Manifest v3 Chrome extension that {does X} on selected pages. Popup UI "
            "+ content script + background service worker. Auth against our API, "
            "settings persisted, submitted to the Chrome Web Store."
        ),
    },
    # ---------------- Backend ----------------
    {
        "title": "REST API for mobile app",
        "category": "Backend",
        "description_template": (
            "Design and implement a REST API: auth, users, core entities, and "
            "OpenAPI docs. Postgres + your favourite framework. Include pagination, "
            "error contract, request validation, and a Postman collection."
        ),
    },
    {
        "title": "GraphQL gateway over existing services",
        "category": "Backend",
        "description_template": (
            "Stand up a GraphQL gateway in front of 3 existing REST services. "
            "Schema-first (Apollo or Yoga), DataLoader for N+1, persisted queries, "
            "JWT auth, integration tests against mocked downstreams."
        ),
    },
    {
        "title": "Stripe billing + webhooks integration",
        "category": "Backend",
        "description_template": (
            "Wire up Stripe Checkout + Billing for subscriptions (3 plans, trial, "
            "proration). Handle webhooks (invoice.paid, sub updated/cancelled) with "
            "idempotency, retries, and a billing portal link. Test with the CLI."
        ),
    },
    {
        "title": "Multi-tenant auth + RBAC",
        "category": "Backend",
        "description_template": (
            "Add multi-tenant auth: organizations, invites, roles (owner/admin/member), "
            "row-level scoping in Postgres. SSO ready (OIDC). Provide a permissions "
            "decorator/middleware and full test coverage."
        ),
    },
    {
        "title": "Full-text search with Postgres / Meilisearch",
        "category": "Backend",
        "description_template": (
            "Add fast, typo-tolerant search over ~500k records. Evaluate Postgres "
            "FTS vs Meilisearch / Typesense, implement the chosen path, expose a "
            "search endpoint with filters/facets, and backfill the index."
        ),
    },
    {
        "title": "Background jobs system",
        "category": "Backend",
        "description_template": (
            "Introduce a background-jobs system (Celery / RQ / Sidekiq / BullMQ) "
            "with retries, dead-letter queue, scheduled jobs, and a dashboard. "
            "Migrate 3 existing sync tasks (emails, exports, webhooks)."
        ),
    },
    {
        "title": "File upload + S3 pipeline",
        "category": "Backend",
        "description_template": (
            "Direct-to-S3 uploads with presigned URLs, virus scanning (ClamAV or "
            "Lambda hook), image thumbnails via libvips/Sharp, and an attachments "
            "table that records owner, size, mime, and lifecycle policy."
        ),
    },
    {
        "title": "Realtime websockets layer",
        "category": "Backend",
        "description_template": (
            "Add a websocket layer for live updates (notifications, presence, chat). "
            "Stack open (Socket.IO / ws / Phoenix Channels). Auth via JWT, Redis "
            "pub/sub fan-out, reconnection + heartbeat handled."
        ),
    },
    {
        "title": "Legacy monolith carve-out",
        "category": "Backend",
        "description_template": (
            "Carve a bounded context (e.g. billing or notifications) out of our "
            "monolith into its own service. Define the API contract, dual-write "
            "during cutover, backfill, then flip reads. Zero downtime."
        ),
    },
    {
        "title": "API rate-limiting + observability",
        "category": "Backend",
        "description_template": (
            "Per-tenant + per-IP rate limits (Redis token bucket), structured "
            "logging, request IDs, OpenTelemetry traces shipped to Tempo/Honeycomb, "
            "and a basic SLO dashboard for the top 10 endpoints."
        ),
    },
    {
        "title": "Public API v1 with SDKs",
        "category": "Backend",
        "description_template": (
            "Design and ship a public API: versioning policy, auth (API keys + "
            "OAuth), rate limits, OpenAPI 3 spec, autogenerated TypeScript + Python "
            "SDKs, and developer docs (Mintlify / Redoc)."
        ),
    },
    # ---------------- Bots ----------------
    {
        "title": "Telegram bot MVP",
        "category": "Bots",
        "description_template": (
            "Build a Telegram bot that {does X}. Include /start, menu, and "
            "1-2 core flows. Persistence in Postgres. Deploy with restart policy "
            "and basic admin commands."
        ),
    },
    {
        "title": "Telegram Mini App (Web App)",
        "category": "Bots",
        "description_template": (
            "Build a Telegram Mini App for {use case}: React + Telegram WebApp SDK, "
            "initData HMAC validation on the backend, theme-aware UI, MainButton + "
            "BackButton wiring, deep linking from the bot."
        ),
    },
    {
        "title": "Telegram customer-support bot",
        "category": "Bots",
        "description_template": (
            "Bot that takes user questions, classifies them, routes to a human "
            "agent group with claim/resolve actions, and stores transcripts. SLA "
            "timers, canned replies, CSAT collection at the end."
        ),
    },
    {
        "title": "Discord moderation + community bot",
        "category": "Bots",
        "description_template": (
            "Discord.js bot: slash commands, role-gated channels, automod rules, "
            "leveling / XP, scheduled announcements, ticket system. Postgres for "
            "persistence, Docker deployment, basic web admin."
        ),
    },
    {
        "title": "WhatsApp Business API integration",
        "category": "Bots",
        "description_template": (
            "Integrate WhatsApp Cloud API (Meta) for customer messaging: opt-in, "
            "template messages, inbound webhook, conversation threading into our "
            "CRM, support for media and quick-reply buttons."
        ),
    },
    {
        "title": "Slack workflow + slash commands",
        "category": "Bots",
        "description_template": (
            "Slack app with slash commands, interactive modals, and event "
            "subscriptions. Use cases: deploy approvals, on-call swaps, weekly "
            "standup collector. OAuth install flow + per-workspace settings."
        ),
    },
    {
        "title": "Lead-capture bot with CRM sync",
        "category": "Bots",
        "description_template": (
            "Telegram or WhatsApp bot that qualifies leads with a short "
            "questionnaire and pushes them into HubSpot / Pipedrive / Notion. "
            "Tag by source, retry on API failure, weekly summary to sales."
        ),
    },
    {
        "title": "Scheduled-reminder / habit bot",
        "category": "Bots",
        "description_template": (
            "Bot that lets users set recurring reminders (daily standup, water, "
            "meds, etc.), timezone-aware, snooze + complete actions, weekly "
            "stats. Persistence + cron scheduler."
        ),
    },
    {
        "title": "E-commerce order-status bot",
        "category": "Bots",
        "description_template": (
            "Bot that lets shoppers check order status, get shipping updates, and "
            "open returns. Pulls from Shopify / WooCommerce API, sends proactive "
            "push on shipped/delivered events."
        ),
    },
    {
        "title": "FAQ / knowledge-base bot",
        "category": "Bots",
        "description_template": (
            "Bot answering FAQs from a curated knowledge base. Admin UI to edit "
            "Q&A, fallback to human handoff, weekly report on unanswered queries "
            "so the KB can be improved."
        ),
    },
    {
        "title": "In-bot payments (Telegram Payments / Stars)",
        "category": "Bots",
        "description_template": (
            "Add paid features to an existing Telegram bot: products, invoice flow, "
            "successful_payment webhook, refunds, receipts. Support either Telegram "
            "Payments (Stripe provider) or Stars."
        ),
    },
    # ---------------- Mobile ----------------
    {
        "title": "Mobile app (iOS+Android) MVP",
        "category": "Mobile",
        "description_template": (
            "Cross-platform mobile MVP (React Native or Flutter). Auth, "
            "list view, detail view, and 1 core action. App icon, splash, and "
            "basic onboarding screens."
        ),
    },
    {
        "title": "Offline-first sync for mobile",
        "category": "Mobile",
        "description_template": (
            "Add offline-first behavior: local SQLite/WatermelonDB, optimistic "
            "writes, queued sync on reconnect, conflict resolution policy. Apply "
            "to the 2-3 most-used screens."
        ),
    },
    {
        "title": "Push notifications (FCM + APNs)",
        "category": "Mobile",
        "description_template": (
            "End-to-end push setup: APNs certs, FCM, device-token registration, "
            "topic + per-user channels, deep-link handling, foreground/background/quit "
            "states. Test plan included."
        ),
    },
    {
        "title": "App Store + Play Store submission",
        "category": "Mobile",
        "description_template": (
            "Prepare and submit an existing build to both stores: bundle IDs, "
            "signing, App Store Connect / Play Console setup, screenshots in all "
            "required sizes, privacy disclosures, response to review feedback."
        ),
    },
    {
        "title": "iOS home-screen widget",
        "category": "Mobile",
        "description_template": (
            "Native iOS widget (WidgetKit / Swift) for an existing RN/Flutter app. "
            "Small + medium sizes, deep link into the app, timeline refresh every "
            "15 min, shared App Group for data."
        ),
    },
    {
        "title": "In-app purchases / subscriptions",
        "category": "Mobile",
        "description_template": (
            "Add IAP via RevenueCat (or native StoreKit2 + Billing): 2 subscription "
            "tiers, free trial, restore purchases, server-side receipt validation, "
            "entitlement state synced with backend."
        ),
    },
    {
        "title": "Maps + geolocation feature",
        "category": "Mobile",
        "description_template": (
            "Map screen with markers, clustering, user location, distance/ETA. "
            "Mapbox or Google Maps. Background location updates with permission "
            "rationale and battery-friendly defaults."
        ),
    },
    {
        "title": "Biometric auth + secure storage",
        "category": "Mobile",
        "description_template": (
            "Face ID / Touch ID / fingerprint to unlock the app, fall back to PIN. "
            "Tokens in Keychain / EncryptedSharedPreferences. Auto-lock after N min "
            "in background."
        ),
    },
    {
        "title": "Audio / video recording feature",
        "category": "Mobile",
        "description_template": (
            "In-app audio (and optionally short video) recording with waveform, "
            "pause/resume, trim, upload with progress + resume. Permissions "
            "handled gracefully on iOS + Android."
        ),
    },
    {
        "title": "React Native / Flutter version upgrade",
        "category": "Mobile",
        "description_template": (
            "Upgrade RN (or Flutter) by 2+ major versions. Update native deps, "
            "fix breaking changes, migrate any deprecated APIs, smoke-test all "
            "screens, ship a build to TestFlight + Play internal."
        ),
    },
    # ---------------- DevOps ----------------
    {
        "title": "DevOps: containerize and deploy",
        "category": "DevOps",
        "description_template": (
            "Take existing repo, containerize, set up CI/CD and deploy to "
            "managed Kubernetes / Fly.io / Render. Include health checks, "
            "secrets, and a one-click rollback path."
        ),
    },
    {
        "title": "GitHub Actions CI/CD pipeline",
        "category": "DevOps",
        "description_template": (
            "Author CI: lint, type-check, tests (parallelized), build, container "
            "publish, deploy to staging on main and to prod on tag. Caching, "
            "matrix builds, required checks on PRs."
        ),
    },
    {
        "title": "Kubernetes migration",
        "category": "DevOps",
        "description_template": (
            "Migrate services from VMs / Docker Compose to a managed Kubernetes "
            "cluster (EKS / GKE / DOKS). Helm charts, ingress + TLS, HPA, "
            "secrets via External Secrets, zero-downtime cutover plan."
        ),
    },
    {
        "title": "Terraform / IaC for cloud infra",
        "category": "DevOps",
        "description_template": (
            "Codify our cloud infra in Terraform: VPC, RDS, S3, IAM, ECR/ECS, "
            "DNS. Remote state, per-env workspaces, drift detection, PR plan "
            "preview via Atlantis or tfaction."
        ),
    },
    {
        "title": "Secrets management with Vault / SOPS",
        "category": "DevOps",
        "description_template": (
            "Move secrets out of .env files and CI variables into Vault (or SOPS + "
            "age). Rotate credentials, document the workflow for devs, integrate "
            "with deploys."
        ),
    },
    {
        "title": "Observability stack (Prom / Grafana / Loki)",
        "category": "DevOps",
        "description_template": (
            "Stand up metrics + logs + traces: Prometheus, Grafana dashboards "
            "(RED + USE), Loki for logs, Tempo or Jaeger for traces. Alert "
            "rules for the top 5 services, paging via PagerDuty / Opsgenie."
        ),
    },
    {
        "title": "Cloud cost optimization audit",
        "category": "DevOps",
        "description_template": (
            "Audit AWS / GCP bill. Identify top 10 cost drivers, propose "
            "rightsizing, savings plans / committed use, S3 lifecycle, idle "
            "resources to delete. Deliver a written report with quantified savings."
        ),
    },
    {
        "title": "Blue/green or canary release setup",
        "category": "DevOps",
        "description_template": (
            "Add safer deploys: blue/green (via load balancer target groups) or "
            "canary (Argo Rollouts / Flagger). Automated health checks, auto-rollback "
            "on error-rate breach, runbook for manual overrides."
        ),
    },
    {
        "title": "On-call setup + runbooks",
        "category": "DevOps",
        "description_template": (
            "Establish an on-call rotation in PagerDuty / Opsgenie. Define "
            "severities, escalation, paging policies. Write runbooks for the top "
            "10 alerts. Postmortem template + blameless review process."
        ),
    },
    {
        "title": "Disaster recovery + backup automation",
        "category": "DevOps",
        "description_template": (
            "Automate backups (Postgres + object storage), encrypted offsite copy, "
            "restore-tested monthly. Document RPO/RTO. Run a tabletop DR exercise "
            "and capture findings."
        ),
    },
    # ---------------- Data ----------------
    {
        "title": "Data pipeline (ETL)",
        "category": "Data",
        "description_template": (
            "Build an ETL pipeline pulling from {sources}, transforming and "
            "loading into Postgres / BigQuery. Schedule via cron or Airflow. "
            "Include retries, alerting on failure, and a small data-quality test suite."
        ),
    },
    {
        "title": "dbt models + tests for warehouse",
        "category": "Data",
        "description_template": (
            "Set up dbt against our warehouse (Snowflake / BigQuery / Postgres). "
            "Build staging + marts layers for 4-6 source systems, add freshness "
            "and schema tests, document models with descriptions and exposures."
        ),
    },
    {
        "title": "Metabase / Superset dashboards",
        "category": "Data",
        "description_template": (
            "Stand up Metabase (or Superset), connect to the warehouse, build 5 "
            "executive dashboards (revenue, funnel, retention, support, ops) on "
            "top of agreed metrics."
        ),
    },
    {
        "title": "Airflow DAG cleanup + refactor",
        "category": "Data",
        "description_template": (
            "Inherit a messy Airflow project. Split monolithic DAGs, parameterize "
            "with TaskFlow, add SLAs and on-failure callbacks, upgrade to "
            "latest stable Airflow, document each pipeline."
        ),
    },
    {
        "title": "Data-quality monitoring",
        "category": "Data",
        "description_template": (
            "Add data-quality checks across critical tables: freshness, row "
            "counts, null rates, uniqueness, referential integrity. Tooling open "
            "(Great Expectations, Soda, Elementary). Alerts into Slack."
        ),
    },
    {
        "title": "Customer segmentation pipeline",
        "category": "Data",
        "description_template": (
            "Build a segmentation pipeline (active / churned / power users / etc.) "
            "from product events, refreshed daily, exposed as a marts table and "
            "synced to our CRM + marketing tool."
        ),
    },
    {
        "title": "Event tracking with Segment / RudderStack",
        "category": "Data",
        "description_template": (
            "Define a tracking plan, instrument the web + mobile apps with "
            "Segment or RudderStack, set up destinations (warehouse, GA4, "
            "marketing tools). Deliver QA checklist + tracking docs."
        ),
    },
    {
        "title": "Reverse-ETL from warehouse to ops tools",
        "category": "Data",
        "description_template": (
            "Sync warehouse models (Customer 360, lead score, MRR) back into "
            "HubSpot / Salesforce / Intercom via Hightouch or Census. Define "
            "the schedule, error handling, and which fields are source-of-truth."
        ),
    },
    {
        "title": "ML feature store + training pipeline",
        "category": "Data",
        "description_template": (
            "Set up a lightweight feature store (Feast or in-warehouse), build "
            "training pipeline for one model end-to-end (data → features → train → "
            "evaluate → register), and deploy a batch-scoring job."
        ),
    },
    {
        "title": "Postgres → analytics warehouse sync",
        "category": "Data",
        "description_template": (
            "Replicate production Postgres into a warehouse (BigQuery / Snowflake / "
            "Redshift) using Fivetran / Airbyte / pg_logical. Backfill, monitor "
            "lag, and document the schema mapping."
        ),
    },
    # ---------------- Design ----------------
    {
        "title": "UI/UX redesign for an internal tool",
        "category": "Design",
        "description_template": (
            "Audit current UX, propose redesign, deliver Figma mocks for "
            "the main screens plus a small design system. Hand off with specs, "
            "states, and tokens ready for engineering."
        ),
    },
    {
        "title": "Mobile app UI/UX from scratch",
        "category": "Design",
        "description_template": (
            "Design a mobile app from scratch: user flows, wireframes, hi-fi UI "
            "in Figma for 10-15 screens (iOS + Android variants where they "
            "differ), prototype, and a starter component library."
        ),
    },
    {
        "title": "Design-system bootstrap (Figma + tokens)",
        "category": "Design",
        "description_template": (
            "Build a design system from our current product: color/type/spacing "
            "tokens, foundational components (Button, Input, Card, Modal, Nav), "
            "documentation in Figma, and JSON token export for engineering."
        ),
    },
    {
        "title": "Landing redesign for conversion",
        "category": "Design",
        "description_template": (
            "Redesign our main landing for sign-up conversion. Includes a brief "
            "audit (heatmap + analytics review), 2 hi-fi directions, the chosen "
            "direction polished, and a fully-spec'd handoff."
        ),
    },
    {
        "title": "Dashboard information architecture rework",
        "category": "Design",
        "description_template": (
            "Rework the IA of our cluttered dashboard: navigation, grouping, "
            "empty states, density. Deliver wireframes, validated with 5 users, "
            "then hi-fi Figma + interaction notes."
        ),
    },
    {
        "title": "Onboarding flow design",
        "category": "Design",
        "description_template": (
            "Design an onboarding flow that gets users to first value fast: "
            "welcome → setup steps → activation moment. Include empty states, "
            "tooltips/checklists, and the rationale for each step."
        ),
    },
    {
        "title": "Illustration / icon pack",
        "category": "Design",
        "description_template": (
            "Custom illustration set (~10 spot illustrations) and a 30-icon set "
            "matching our brand. Delivered as Figma + SVG, with light/dark "
            "variants and naming conventions."
        ),
    },
    {
        "title": "Dark-mode pass on existing product",
        "category": "Design",
        "description_template": (
            "Audit our product and produce a dark-mode pass: color tokens, "
            "contrast checks, updated illustrations/icons, edge cases (modals, "
            "charts, hover states), and a handoff doc."
        ),
    },
    {
        "title": "Figma → design tokens handoff",
        "category": "Design",
        "description_template": (
            "Restructure our messy Figma file with styles + variables, export "
            "design tokens (Style Dictionary / Token Studio), and align names "
            "with the front-end's Tailwind / CSS-vars setup."
        ),
    },
    {
        "title": "Accessibility / WCAG design review",
        "category": "Design",
        "description_template": (
            "Review our designs against WCAG 2.1 AA from a design perspective: "
            "contrast, hit areas, focus states, motion, error patterns. Deliver "
            "a prioritized list of design fixes with Figma examples."
        ),
    },
    # ---------------- AI ----------------
    {
        "title": "AI integration (LLM-powered feature)",
        "category": "AI",
        "description_template": (
            "Integrate an LLM into an existing product to power {feature}. "
            "Prompt engineering, evaluation, and basic guardrails. Provider "
            "choice open (Anthropic / OpenAI / open-weights)."
        ),
    },
    {
        "title": "RAG assistant over internal docs",
        "category": "AI",
        "description_template": (
            "Build a retrieval-augmented assistant over our docs / wiki / "
            "support tickets. Ingestion pipeline, chunking + embeddings, hybrid "
            "search, answer with citations, eval set of 50 Q&A pairs."
        ),
    },
    {
        "title": "Customer-support chatbot with handoff",
        "category": "AI",
        "description_template": (
            "LLM chatbot for tier-1 support: grounded on our help center, can "
            "open / update tickets, escalates to a human with full context when "
            "confidence is low or the user asks."
        ),
    },
    {
        "title": "Voice agent for inbound calls",
        "category": "AI",
        "description_template": (
            "Voice agent (Twilio / Vapi / LiveKit + LLM + TTS/STT) that handles "
            "common inbound calls: appointment booking, status checks, FAQs. "
            "Latency under 1s, transcript stored, escalation to human."
        ),
    },
    {
        "title": "Fine-tuning on domain data",
        "category": "AI",
        "description_template": (
            "Fine-tune a small open-weights model (Llama / Mistral / Qwen) on "
            "our domain data for {task}. Data prep, training run, evaluation "
            "against a held-out set, comparison vs prompted baseline."
        ),
    },
    {
        "title": "Image generation pipeline",
        "category": "AI",
        "description_template": (
            "Image generation pipeline (SDXL / Flux / Imagen) for a product use "
            "case. Prompt + style presets, queueing for long runs, S3 storage, "
            "moderation, and a small admin UI."
        ),
    },
    {
        "title": "AI-powered search / semantic search",
        "category": "AI",
        "description_template": (
            "Add semantic search to an existing catalog. Embeddings of items + "
            "queries, vector store (pgvector / Qdrant), reranker, evaluation on "
            "a labeled set. Drop-in API for the frontend."
        ),
    },
    {
        "title": "Eval harness + guardrails for an LLM feature",
        "category": "AI",
        "description_template": (
            "Build an offline eval harness for an existing LLM feature: golden "
            "set, automated rubric scoring, regression CI, plus runtime "
            "guardrails (PII filter, jailbreak detection, output validation)."
        ),
    },
    {
        "title": "Prompt + cost optimization",
        "category": "AI",
        "description_template": (
            "Audit our LLM calls: reduce token usage with caching, prompt "
            "trimming, smarter model routing (small model first, escalate on "
            "uncertainty). Target 40%+ cost cut with no quality regression."
        ),
    },
    {
        "title": "Multimodal document parser",
        "category": "AI",
        "description_template": (
            "Parse messy PDFs / scans / images (invoices, contracts, receipts) "
            "into structured JSON using a vision-capable LLM + OCR fallback. "
            "Evaluation on labeled samples, confidence scoring, human review queue."
        ),
    },
    {
        "title": "AI agent for internal workflows",
        "category": "AI",
        "description_template": (
            "Build an agent that automates a multi-step internal workflow (e.g. "
            "lead triage, ticket categorization, weekly reporting). Tool use, "
            "guardrails, observability, and a clear human-in-the-loop checkpoint."
        ),
    },
]
