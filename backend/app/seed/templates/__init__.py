"""Curated project templates surfaced to customers when creating a project.

The canonical row in ``project_templates`` carries the English title +
description (kept stable as the lookup key). Per-locale title/description
overrides live in ``project_template_translations`` and are loaded from
``en.py`` / ``ru.py``. The seed loader inserts the canonical row keyed on
the English title and then upserts one translation row per supported locale.
"""

from __future__ import annotations

from app.seed.templates.en import PROJECT_TEMPLATES_EN
from app.seed.templates.ru import PROJECT_TEMPLATES_RU

PROJECT_TEMPLATES: list[dict[str, str]] = PROJECT_TEMPLATES_EN

LOCALIZED_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "en": PROJECT_TEMPLATES_EN,
    "ru": PROJECT_TEMPLATES_RU,
}

__all__ = ["PROJECT_TEMPLATES", "LOCALIZED_TEMPLATES"]
