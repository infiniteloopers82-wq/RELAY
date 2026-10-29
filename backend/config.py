
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    # Use PostgreSQL in production when DATABASE_URL is configured.
    # Fall back to a local SQLite database for development.
    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql://", 1
        )

    SQLALCHEMY_DATABASE_URI = (
        database_url
        or f"sqlite:///{BASE_DIR / 'relay.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv(
        "SESSION_COOKIE_SAMESITE", "Lax"
    )
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "false").lower()
        == "true"
    )

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            (
                "http://localhost:5173,"
                "http://127.0.0.1:5173,"
                "http://localhost:5174,"
                "http://127.0.0.1:5174"
            ),
        ).split(",")
        if origin.strip()
    ]

    MAX_ACTIVE_BOOKINGS_PER_USER = int(
        os.getenv("MAX_ACTIVE_BOOKINGS_PER_USER", "3")
    )
