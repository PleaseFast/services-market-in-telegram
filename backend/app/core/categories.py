"""Closed-vocabulary project/specialist categories and a lightweight keyword
classifier used to auto-assign a category to manually-created projects.

This is the single source of truth on the server side. The frontend mirrors
the same closed list in ``frontend/src/lib/categories.ts`` — keep both in sync.

Category IDs stay English so they're stable across languages (storage,
filters, indexes, query params). Localized display labels live in
``CATEGORY_LABELS`` and are resolved per request from the caller's language.
"""

from __future__ import annotations

from app.core.i18n import DEFAULT as DEFAULT_LANG
from app.core.i18n import SUPPORTED as SUPPORTED_LANGS

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


CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "ru": {
        "Frontend": "Фронтенд",
        "Backend": "Бэкенд",
        "Bots": "Боты",
        "Mobile": "Мобильная разработка",
        "DevOps": "DevOps",
        "Data": "Данные",
        "Design": "Дизайн",
        "AI": "ИИ",
        "Other": "Другое",
    },
    "en": {c: c for c in CATEGORIES},
}


def label_for(category: str, lang: str = DEFAULT_LANG) -> str:
    """Return the human-readable label for ``category`` in ``lang``.

    Falls back to the English label (i.e. the canonical ID) for unknown
    languages or categories so callers always get a printable string.
    """
    lang_key = lang if lang in SUPPORTED_LANGS else DEFAULT_LANG
    table = CATEGORY_LABELS.get(lang_key, CATEGORY_LABELS[DEFAULT_LANG])
    return table.get(category, category)


# Keyword tables are intentionally lowercase. Match is plain substring on the
# concatenated lowercase ``title + " " + description``. Multi-word keywords
# are fine — they just won't match on partial words. Russian entries make the
# classifier work on Russian project briefs without needing per-language
# pipelines.
KEYWORDS: dict[str, tuple[str, ...]] = {
    "Bots": (
        "telegram bot",
        "aiogram",
        "chatbot",
        "bot",
        "discord bot",
        "whatsapp bot",
        "slack bot",
        "бот",
        "телеграм-бот",
        "телеграм бот",
        "чат-бот",
        "дискорд-бот",
        "вотсап-бот",
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
        "фронтенд",
        "фронт-энд",
        "лендинг",
        "верстка",
        "вёрстка",
        "интерфейс",
        "веб-интерфейс",
        "дашборд",
        "одностраничник",
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
        "бэкенд",
        "бек-энд",
        "сервер",
        "серверная часть",
        "микросервис",
        "апи",
    ),
    "Mobile": (
        "ios",
        "android",
        "react native",
        "flutter",
        "swift",
        "kotlin",
        "mobile app",
        "мобильное приложение",
        "мобильная разработка",
        "андроид",
        "айос",
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
        "девопс",
        "инфраструктура",
        "кубернетес",
        "терраформ",
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
        "данные",
        "хранилище данных",
        "аналитика",
        "etl-пайплайн",
        "пайплайн данных",
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
        "дизайн",
        "фигма",
        "логотип",
        "айдентика",
        "брендинг",
        "иллюстрация",
        "ux-дизайн",
        "юай-кит",
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
        "ии",
        "искусственный интеллект",
        "машинное обучение",
        "нейросеть",
        "нейронн",
        "ллм",
        "эмбеддинг",
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
