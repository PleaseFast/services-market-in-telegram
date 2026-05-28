"""Canonical service catalog: category -> subcategory -> service.

This is the single source of truth on the server side. The frontend mirrors
the same closed list in ``frontend/src/lib/serviceCatalog.ts`` — keep both in
sync. The DB ``service_catalog`` table is populated from this list by the seed
runner (idempotent dedupe by slug).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceCatalogEntry:
    slug: str
    category: str
    subcategory: str
    label: str


def _entries(category: str, subcategory: str, services: list[str]) -> list[ServiceCatalogEntry]:
    """Helper: derive a stable slug from the (category, subcategory, label)
    triple. The slug is what binds a service to a specialist; renaming a label
    later doesn't invalidate any selections."""
    out: list[ServiceCatalogEntry] = []
    for label in services:
        slug_label = (
            label.lower()
            .replace("/", "-")
            .replace("&", "and")
            .replace("+", "plus")
            .replace(" ", "-")
            .replace("(", "")
            .replace(")", "")
        )
        slug_sub = subcategory.lower().replace(" ", "-")
        slug_cat = category.lower()
        out.append(
            ServiceCatalogEntry(
                slug=f"{slug_cat}.{slug_sub}.{slug_label}",
                category=category,
                subcategory=subcategory,
                label=label,
            )
        )
    return out


SERVICE_CATALOG: list[ServiceCatalogEntry] = [
    # --- Design ---------------------------------------------------------
    *_entries("Design", "Web Design", [
        "Landing page design",
        "Chat UI design",
        "Dashboard UI design",
        "E-commerce storefront design",
        "Marketing site redesign",
    ]),
    *_entries("Design", "Graphic Design", [
        "Logo design",
        "Brand packaging",
        "Illustrations",
        "Social media kit",
    ]),
    *_entries("Design", "UX Design", [
        "User flows",
        "Wireframes",
        "Usability audit",
        "Design system documentation",
    ]),

    # --- Frontend -------------------------------------------------------
    *_entries("Frontend", "Web Apps", [
        "SPA from scratch",
        "Migration to React",
        "Migration to Next.js",
        "Real-time UI",
    ]),
    *_entries("Frontend", "Landing Pages", [
        "Marketing landing page",
        "Pricing page",
        "Documentation site",
    ]),
    *_entries("Frontend", "Admin Dashboards", [
        "Admin panel",
        "Analytics dashboard",
        "Internal tools",
    ]),
    *_entries("Frontend", "Component Libraries", [
        "Design system kit",
        "Storybook setup",
        "Headless component library",
    ]),

    # --- Backend --------------------------------------------------------
    *_entries("Backend", "APIs", [
        "REST API",
        "GraphQL API",
        "WebSocket service",
        "API redesign",
    ]),
    *_entries("Backend", "Integrations", [
        "Stripe integration",
        "OpenAI integration",
        "Telegram integration",
        "Third-party CRM integration",
    ]),
    *_entries("Backend", "Auth", [
        "OAuth integration",
        "SSO setup",
        "Role-based access control",
    ]),
    *_entries("Backend", "Infrastructure", [
        "Database schema design",
        "Migrations and backfills",
        "Background job system",
    ]),

    # --- Bots -----------------------------------------------------------
    *_entries("Bots", "Telegram Bots", [
        "Bot from scratch",
        "Aiogram FSM workflow",
        "Webhook integration",
        "Bot migration to aiogram 3",
    ]),
    *_entries("Bots", "Other Platforms", [
        "Discord bot",
        "Slack bot",
        "WhatsApp bot",
    ]),
    *_entries("Bots", "Bot Integrations", [
        "Payments inside bot",
        "Bot to CRM bridge",
        "Bot analytics",
    ]),

    # --- Mobile ---------------------------------------------------------
    *_entries("Mobile", "iOS", [
        "Native iOS app",
        "iOS app refactor",
        "App Store submission",
    ]),
    *_entries("Mobile", "Android", [
        "Native Android app",
        "Android app refactor",
        "Play Store submission",
    ]),
    *_entries("Mobile", "Cross-platform", [
        "React Native app",
        "Flutter app",
        "Hybrid web wrapper",
    ]),

    # --- DevOps ---------------------------------------------------------
    *_entries("DevOps", "CI and CD", [
        "GitHub Actions setup",
        "CI pipeline overhaul",
        "Release automation",
    ]),
    *_entries("DevOps", "Cloud", [
        "AWS setup",
        "GCP setup",
        "Cloud migration",
    ]),
    *_entries("DevOps", "Containers", [
        "Docker setup",
        "Kubernetes deployment",
        "Helm chart authoring",
    ]),
    *_entries("DevOps", "Infrastructure as Code", [
        "Terraform setup",
        "Ansible automation",
    ]),
    *_entries("DevOps", "Observability", [
        "Logging pipeline",
        "Metrics and alerting",
        "Tracing setup",
    ]),

    # --- Data -----------------------------------------------------------
    *_entries("Data", "Pipelines", [
        "ETL pipeline",
        "Airflow DAG authoring",
        "Streaming pipeline",
    ]),
    *_entries("Data", "Warehousing", [
        "Snowflake setup",
        "BigQuery setup",
        "Data warehouse migration",
    ]),
    *_entries("Data", "Analytics", [
        "Analytics dashboard",
        "Custom reporting",
        "Data audit",
    ]),

    # --- AI -------------------------------------------------------------
    *_entries("AI", "LLM Integration", [
        "OpenAI integration",
        "Anthropic integration",
        "Self-hosted LLM setup",
    ]),
    *_entries("AI", "RAG", [
        "Document RAG system",
        "Knowledge-base assistant",
        "Vector DB setup",
    ]),
    *_entries("AI", "ML Models", [
        "Model fine-tuning",
        "Embedding pipeline",
        "Recommendation engine",
    ]),
    *_entries("AI", "Conversational AI", [
        "AI chatbot",
        "Voice assistant",
    ]),

    # --- Other ----------------------------------------------------------
    *_entries("Other", "Consulting", [
        "Technical consulting",
        "Code review",
        "Architecture review",
    ]),
    *_entries("Other", "Mentoring", [
        "1:1 mentoring",
        "Team training",
    ]),
    *_entries("Other", "Writing", [
        "Technical writing",
        "API documentation",
    ]),
]


SERVICE_CATALOG_BY_SLUG: dict[str, ServiceCatalogEntry] = {e.slug: e for e in SERVICE_CATALOG}
