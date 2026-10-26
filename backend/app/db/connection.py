"""
Database connection manager with Two-Tier Storage Architecture:
1. Primary: PostgreSQL (production-grade relational database).
2. Backup / Fallback: SQLite ('docuintel.db' local file for high availability).

The system always checks and attempts the PostgreSQL connection first.
If PostgreSQL is unreachable, credentials fail, or server is offline,
it seamlessly switches to the SQLite backup so the platform never crashes.
"""

from __future__ import annotations

import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

SQLITE_BACKUP_URL = "sqlite:///./docuintel.db"


def resolve_database_url() -> str:
    """
    Resolve and normalize the configured database URL.
    Normalizes 'postgres://' or 'postgresql://' -> 'postgresql+psycopg2://'.
    If omitted or empty, defaults to SQLite backup URL.
    """
    raw_url = settings.DATABASE_URL

    if raw_url and raw_url.strip():
        url = raw_url.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    return SQLITE_BACKUP_URL


# Resolve initial target URL
DB_URL = resolve_database_url()
is_sqlite = DB_URL.startswith("sqlite")

engine_args = {}
if is_sqlite:
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args["pool_pre_ping"] = True
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20
    # Fast 5-second connection timeout to prevent hanging if PostgreSQL is down
    engine_args["connect_args"] = {"connect_timeout": 5}

engine = create_engine(DB_URL, **engine_args)
_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db_initialized = False


def get_active_backend_name() -> str:
    """Return the name of the active database backend."""
    return "SQLite (Backup)" if is_sqlite else "PostgreSQL (Primary)"


def is_using_sqlite_backup() -> bool:
    """Check if the system is currently using the SQLite backup."""
    return is_sqlite


def switch_to_sqlite_backup(reason: str = "") -> None:
    """Explicitly switch the active engine and session factory to local SQLite backup."""
    global engine, _session_factory, DB_URL, is_sqlite, _db_initialized

    logger.warning(
        f"[DB Failover] Primary PostgreSQL unavailable ({reason}). "
        f"Switching to SQLite backup database ({SQLITE_BACKUP_URL}) to guarantee 100% uptime."
    )
    DB_URL = SQLITE_BACKUP_URL
    is_sqlite = True
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
    _session_factory.configure(bind=engine)

    import app.db.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("[DB Failover] SQLite backup database initialized successfully.")
    _db_initialized = True


def SessionLocal() -> Session:
    """Create a new database session bound to the active engine."""
    global _db_initialized
    if not _db_initialized:
        init_db()
    return _session_factory()


def init_db(force_sqlite: bool = False) -> None:
    """
    Initialize the database:
    1. First check the primary PostgreSQL connection.
    2. If PostgreSQL connects, initialize tables on PostgreSQL.
    3. If PostgreSQL connection fails (or force_sqlite is True), gracefully move to SQLite backup.
    """
    global engine, _session_factory, DB_URL, is_sqlite, _db_initialized

    if _db_initialized and not force_sqlite:
        return

    import app.db.models  # noqa: F401

    if force_sqlite:
        switch_to_sqlite_backup("Forced SQLite backup initialization")
        return

    # Check Primary: PostgreSQL
    if not is_sqlite:
        try:
            logger.info(f"[DB] Checking primary PostgreSQL connection at {DB_URL.split('@')[-1]}...")
            with engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            Base.metadata.create_all(bind=engine)
            target = DB_URL.split("@")[-1] if "@" in DB_URL else DB_URL
            logger.info(f"[DB] SUCCESS: Primary PostgreSQL database connected and initialized: {target}")
            _db_initialized = True
            return
        except Exception as e:
            # PostgreSQL check failed -> Move to SQLite backup
            switch_to_sqlite_backup(str(e))
            return

    # Direct SQLite (if no PostgreSQL URL was configured)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"[DB] SQLite backup database initialized directly ({DB_URL})")
        _db_initialized = True
    except Exception as e:
        logger.error(f"[DB] Error initializing SQLite tables: {e}")


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session per request.
    Includes runtime auto-recovery to SQLite backup if PostgreSQL drops during an active session.
    """
    try:
        db = SessionLocal()
    except Exception as e:
        logger.warning(f"[DB] Session creation error on primary engine: {e}. Recovering via SQLite backup...")
        switch_to_sqlite_backup(str(e))
        db = SessionLocal()

    try:
        yield db
    except Exception as e:
        # Check if error is a connection drop
        err_str = str(e).lower()
        if not is_sqlite and any(k in err_str for k in ["operationalerror", "connection refused", "closed unexpectedly", "terminating connection"]):
            logger.error(f"[DB] Runtime PostgreSQL connection lost: {e}. Switching to SQLite backup for recovery.")
            switch_to_sqlite_backup(str(e))
        raise
    finally:
        db.close()


# Initialize database automatically on startup
try:
    init_db()
except Exception as e:
    logger.warning(f"[DB] Startup initialization handled exception: {e}")


