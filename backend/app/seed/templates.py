"""Curated project templates surfaced to customers when creating a project."""

PROJECT_TEMPLATES: list[dict[str, str]] = [
    {
        "title": "Landing page for SaaS product",
        "category": "Frontend",
        "description_template": (
            "Build a responsive marketing landing page. Sections: hero, features, "
            "pricing, FAQ, footer. Stack open to suggestion (Next.js preferred)."
        ),
    },
    {
        "title": "REST API for mobile app",
        "category": "Backend",
        "description_template": (
            "Design and implement a REST API: auth, users, core entities, and "
            "OpenAPI docs. Postgres + your favourite framework."
        ),
    },
    {
        "title": "Telegram bot MVP",
        "category": "Bots",
        "description_template": (
            "Build a Telegram bot that {does X}. Include /start, menu, and "
            "1-2 core flows. Persistence in Postgres."
        ),
    },
    {
        "title": "Mobile app (iOS+Android) MVP",
        "category": "Mobile",
        "description_template": (
            "Cross-platform mobile MVP (React Native or Flutter). Auth, "
            "list view, detail view, and 1 core action."
        ),
    },
    {
        "title": "DevOps: containerize and deploy",
        "category": "DevOps",
        "description_template": (
            "Take existing repo, containerize, set up CI/CD and deploy to "
            "managed Kubernetes / Fly.io / Render."
        ),
    },
    {
        "title": "Data pipeline (ETL)",
        "category": "Data",
        "description_template": (
            "Build an ETL pipeline pulling from {sources}, transforming and "
            "loading into Postgres / BigQuery. Schedule via cron or Airflow."
        ),
    },
    {
        "title": "UI/UX redesign for an internal tool",
        "category": "Design",
        "description_template": (
            "Audit current UX, propose redesign, deliver Figma mocks for "
            "the main screens plus a small design system."
        ),
    },
    {
        "title": "AI integration (LLM-powered feature)",
        "category": "AI",
        "description_function": (
            "Integrate an LLM into an existing product to power {feature}. "
            "Prompt engineering, evaluation, and basic guardrails."
        ),
    },
]
