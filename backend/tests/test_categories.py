import pytest

from app.core.categories import CATEGORIES, DEFAULT_CATEGORY, clamp_category, suggest_category


@pytest.mark.parametrize(
    "title,description,expected",
    [
        ("Telegram bot for orders", "aiogram fsm", "Bots"),
        ("React dashboard UI", "Tailwind components", "Frontend"),
        ("Stripe API integration", "FastAPI backend", "Backend"),
        ("AI chatbot with RAG", "OpenAI gpt embeddings", "AI"),
        ("iOS app", "Swift, React Native compatible", "Mobile"),
        ("Kubernetes setup", "Docker, Terraform on AWS", "DevOps"),
        ("ETL pipeline", "Airflow + Snowflake analytics", "Data"),
        ("Logo + branding", "Figma design system", "Design"),
        ("", "", DEFAULT_CATEGORY),
        ("totally unrelated", "lorem ipsum dolor sit amet", DEFAULT_CATEGORY),
    ],
)
def test_suggest_category(title: str, description: str, expected: str) -> None:
    assert suggest_category(title, description) == expected


def test_clamp_category_passes_valid() -> None:
    for cat in CATEGORIES:
        assert clamp_category(cat) == cat


def test_clamp_category_falls_back() -> None:
    assert clamp_category(None) == DEFAULT_CATEGORY
    assert clamp_category("") == DEFAULT_CATEGORY
    assert clamp_category("Not-A-Real-Category") == DEFAULT_CATEGORY
