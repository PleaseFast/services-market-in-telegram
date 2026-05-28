"""Closed-vocabulary project/specialist categories and a lightweight keyword
classifier used to auto-assign a category to manually-created projects.

This is the single source of truth on the server side. The frontend mirrors
the same closed list in ``frontend/src/lib/categories.ts`` — keep both in sync.
"""

from __future__ import annotations

CATEGORIES: tuple[str, ...] = (
    "Frontend",
    "Backend",
    "Bots",
    "Mobile",
    "DevOps",
    "Data",
    "Design",
    "AI",
    "Other",
)

DEFAULT_CATEGORY = "Other"

_CATEGORY_SET = set(CATEGORIES)

# Keyword tables are intentionally lowercase. Match is plain substring on the
# concatenated lowercase ``title + " " + description``. Multi-word keywords
# are fine — they just won't match on partial words.
KEYWORDS: dict[str, tuple[str, ...]] = {
    "Bots": (
        "telegram bot",
        "aiogram",
        "chatbot",
        "bot",
        "discord bot",
        "whatsapp bot",
        "slack bot",
    ),
    "Frontend": (
        "react",
        "next.js",
        "nextjs",
        "vue",
        "svelte",
        "tailwind",
        "spa",
        "dashboard",
        "landing page",
        "frontend",
        "front-end",
        "ui ",
        "web ui",
    ),
    "Backend": (
        "fastapi",
        "django",
        "flask",
        "node.js",
        "nodejs",
        "express",
        "stripe",
        "rest api",
        "graphql",
        "postgres",
        "mysql",
        "backend",
        "back-end",
        "microservice",
        " api",
    ),
    "Mobile": (
        "ios",
        "android",
        "react native",
        "flutter",
        "swift",
        "kotlin",
        "mobile app",
    ),
    "DevOps": (
        "docker",
        "kubernetes",
        "k8s",
        "ci/cd",
        "terraform",
        "ansible",
        "aws",
        "gcp",
        "azure",
        "devops",
        "infrastructure",
    ),
    "Data": (
        "etl",
        "airflow",
        "snowflake",
        "bigquery",
        "redshift",
        "data pipeline",
        "analytics",
        "data warehouse",
        "spark",
    ),
    "Design": (
        "figma",
        "logo",
        "ui kit",
        "branding",
        "illustration",
        "design system",
        "ux design",
        "visual design",
    ),
    "AI": (
        "llm",
        "openai",
        "gpt",
        "claude",
        "anthropic",
        "rag",
        "ai chatbot",
        "machine learning",
        "ml model",
        "embedding",
        "vector db",
    ),
}


def clamp_category(value: str | None) -> str:
    """Return ``value`` if it's part of the closed set, else ``DEFAULT_CATEGORY``."""
    if value and value in _CATEGORY_SET:
        return value
    return DEFAULT_CATEGORY


def suggest_category(title: str, description: str = "") -> str:
    """Pick the best-matching category by counting keyword hits.

    Ties are broken by the order categories appear in ``CATEGORIES``. Falls back
    to ``DEFAULT_CATEGORY`` when no keyword matches.
    """
    text = f"{title or ''} {description or ''}".lower()
    if not text.strip():
        return DEFAULT_CATEGORY

    best_category = DEFAULT_CATEGORY
    best_score = 0
    for category in CATEGORIES:
        keywords = KEYWORDS.get(category, ())
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_category = category
    return best_category
