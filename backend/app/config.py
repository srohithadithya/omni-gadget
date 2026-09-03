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
        "postgresql://aideuser:aidepass@localhost:5432/aideosdb"
    )

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # ── API ───────────────────────────────────────────────────────────────────
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list = ["*"]

    # ── GST / Tax constants (India) ───────────────────────────────────────────
    GST_RATE: float = 0.18


@lru_cache()
def get_settings() -> Settings:
    return Settings()
