from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from Arina.database.config import DATABASE_SCHEMA, DATABASE_URL, is_database_configured


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Create or return SQLAlchemy engine."""
    global _engine

    if not is_database_configured():
        raise RuntimeError("ARINA_DATABASE_URL is not configured")

    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            future=True,
            connect_args={"options": f"-csearch_path={DATABASE_SCHEMA},public"},
        )

    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Create or return SQLAlchemy session factory."""
    global _SessionLocal

    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )

    return _SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    """Yield DB session for future Flask/API handlers."""
    session = get_session_factory()()

    try:
        yield session
    finally:
        session.close()


def ping_database() -> bool:
    """Return True when PostgreSQL responds."""
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
