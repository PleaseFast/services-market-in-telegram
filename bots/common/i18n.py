"""Tiny JSON-based translation helper for the three bot processes.

Catalogues live under ``bots/common/locales/{lang}/*.json`` and are loaded
lazily on first use. Keys are dotted paths into the merged catalogue per
language (e.g. ``"doers.menu.open_app"``). Missing keys fall back to the
default language, then to the key itself, so a missing translation always
prints *something* readable rather than crashing the bot.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.core.i18n import DEFAULT, SUPPORTED, normalize

log = logging.getLogger(__name__)

_LOCALES_DIR = Path(__file__).resolve().parent / "locales"

_CATALOGUES: dict[str, dict[str, Any]] = {}


def _load_lang(lang: str) -> dict[str, Any]:
    """Merge every JSON file under ``locales/<lang>/`` into one nested dict."""
    merged: dict[str, Any] = {}
    lang_dir = _LOCALES_DIR / lang
    if not lang_dir.is_dir():
        return merged
    for path in sorted(lang_dir.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as f:
                merged.update(json.load(f))
        except Exception:
            log.exception("Failed to load i18n catalogue %s", path)
    return merged


def _catalogue(lang: str) -> dict[str, Any]:
    if lang not in _CATALOGUES:
        _CATALOGUES[lang] = _load_lang(lang)
    return _CATALOGUES[lang]


def _lookup(catalogue: dict[str, Any], key: str) -> str | None:
    node: Any = catalogue
    for part in key.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
        if node is None:
            return None
    if isinstance(node, str):
        return node
    return None


def t(key: str, lang: str | None = None, **params: Any) -> str:
    """Translate ``key`` into ``lang`` and apply ``str.format`` substitutions.

    Falls back to ``DEFAULT`` and then to the literal ``key`` when missing.
    """
    target = normalize(lang)
    template = _lookup(_catalogue(target), key)
    if template is None and target != DEFAULT:
        template = _lookup(_catalogue(DEFAULT), key)
    if template is None:
        return key
    if not params:
        return template
    try:
        return template.format(**params)
    except (KeyError, IndexError, ValueError):
        log.warning("i18n: bad format params for key %s lang %s: %r", key, target, params)
        return template


def available_languages() -> tuple[str, ...]:
    return SUPPORTED
