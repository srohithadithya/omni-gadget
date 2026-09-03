"""
Central configuration — reads from environment variables with safe defaults.
Copy .env.example → .env and fill in your values before running.
"""
import os
from functools import lru_cache


class Settings:
    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "AIDE-OS"
    APP_VERSION: str = "4.0.0-PROD"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://aideuser:***@localhost:5432/aideosdb"
    )

    @staticmethod
    def _normalize_db_url(url: str) -> str:
        """Normalize database URL: postgres:// -> postgresql://, ensure sslmode=require for cloud DBs."""
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://") and "sslmode=" not in url:
            url += "?sslmode=require"
        return url

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # ── API ───────────────────────────────────────────────────────────────────
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list = ["*"]

    # ── GST / Tax constants (India) ───────────────────────────────────────────
    GST_RATE: float = 0.18


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    s.DATABASE_URL = s._normalize_db_url(s.DATABASE_URL)
    return s
