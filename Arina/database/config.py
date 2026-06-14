import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_SCHEMA = os.getenv("ARINA_DATABASE_SCHEMA", "arina")
DATABASE_URL = os.getenv("ARINA_DATABASE_URL", "").strip()


def is_database_configured() -> bool:
    """Return True when PostgreSQL connection string is configured."""
    return bool(DATABASE_URL)


def get_masked_database_url() -> str:
    """Return a safe database URL representation without password."""
    if not DATABASE_URL:
        return ""

    if "@" not in DATABASE_URL or ":" not in DATABASE_URL:
        return DATABASE_URL

    prefix, suffix = DATABASE_URL.rsplit("@", 1)
    driver_and_user = prefix.split(":", 2)[:2]

    if len(driver_and_user) < 2:
        return f"***@{suffix}"

    return f"{driver_and_user[0]}:{driver_and_user[1]}:***@{suffix}"
