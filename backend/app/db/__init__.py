"""
Database package for DocuIntel AI.
Provides PostgreSQL connection management, SQLAlchemy ORM models, and CRUD operations.
"""

from app.db.connection import (
    Base,
    engine,
    get_db,
    init_db,
    SessionLocal,
    get_active_backend_name,
    is_using_sqlite_backup,
    switch_to_sqlite_backup,
)
from app.db.models import DocumentRecord, AnalysisRecord
from app.db import crud

__all__ = [
    "Base",
    "engine",
    "get_db",
    "init_db",
    "SessionLocal",
    "get_active_backend_name",
    "is_using_sqlite_backup",
    "switch_to_sqlite_backup",
    "DocumentRecord",
    "AnalysisRecord",
    "crud",
]

