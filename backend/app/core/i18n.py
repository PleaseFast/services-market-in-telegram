"""Language detection and normalization for the i18n system.

Russian is the default. English is the only other supported language.
Everything (Telegram language codes, Accept-Language headers, browser
locales) eventually lands here to be normalized to one of those two.
"""

from __future__ import annotations

SUPPORTED: tuple[str, ...] = ("ru", "en")
DEFAULT: str = "ru"


def normalize(code: str | None) -> str:
    """Map a free-form locale string to one of ``SUPPORTED`` or ``DEFAULT``.

    Accepts BCP-47 tags ("ru-RU", "en-US"), Telegram language codes ("ru"),
    or ``None``. The first two letters are the primary subtag; anything we
    don't recognize falls back to ``DEFAULT``.
    """
    if not code:
        return DEFAULT
    primary = code.strip().lower().replace("_", "-").split("-", 1)[0]
    if primary in SUPPORTED:
        return primary
    return DEFAULT


def parse_accept_language(header: str | None) -> str:
    """Pick the first supported language from an Accept-Language header.

    Ignores q-weights — the order the client put them in is good enough for
    a two-language product. Falls back to ``DEFAULT`` if nothing matches.
    """
    if not header:
        return DEFAULT
    for chunk in header.split(","):
        tag = chunk.split(";", 1)[0].strip()
        lang = normalize(tag)
        # ``normalize`` returns DEFAULT for unknowns, so only count a tag as a
        # real match when its primary subtag is itself supported.
        primary = tag.lower().split("-", 1)[0]
        if primary in SUPPORTED:
            return lang
    return DEFAULT
