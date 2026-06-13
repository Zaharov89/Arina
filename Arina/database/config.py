import os


DATABASE_URL = os.getenv("ARINA_DATABASE_URL", "")


def is_database_configured() -> bool:
    """Return True when PostgreSQL connection string is configured."""
    return bool(DATABASE_URL.strip())
