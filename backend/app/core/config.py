from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://doings:doings@postgres:5432/doings"
    DATABASE_URL_SYNC: str = "postgresql+psycopg://doings:doings@postgres:5432/doings"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Auth
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_TTL_MINUTES: int = 30
    REFRESH_TOKEN_TTL_DAYS: int = 14

    # CORS — comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost"

    # Telegram bots
    TG_DOERS_BOT_TOKEN: str = ""
    TG_CUSTOMERS_BOT_TOKEN: str = ""
    TG_REFEREE_BOT_TOKEN: str = ""
    TG_WEBAPP_URL: str = "http://localhost"

    # Rate limit
    RATE_LIMIT_DEFAULT: str = "120/minute"

    APP_ENV: str = Field(default="dev")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def all_bot_tokens(self) -> dict[str, str]:
        return {
            "doers": self.TG_DOERS_BOT_TOKEN,
            "customers": self.TG_CUSTOMERS_BOT_TOKEN,
            "referee": self.TG_REFEREE_BOT_TOKEN,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
