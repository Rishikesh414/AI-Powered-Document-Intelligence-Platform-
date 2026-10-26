"""
CRUD Operations for PostgreSQL / SQLAlchemy database.
Provides basic database functions for documents and analyses:
- create_document, get_document_by_id, get_document_by_hash, list_documents, delete_document
- create_analysis, get_analysis_by_id, get_latest_analysis_for_document, list_analyses_for_document
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models import DocumentRecord, AnalysisRecord

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Document Operations
# ---------------------------------------------------------------------------

def create_document(
    db: Session,
    document_id: str,
    filename: str,
    file_path: str,
    content_hash: str,
    file_size: int,
    extracted_text: str,
    mime_type: str = "application/pdf",
    document_type: Optional[str] = None,
) -> DocumentRecord:
    """Insert a new document record into the database."""
    record = DocumentRecord(
        id=document_id,
        filename=filename,
        file_path=file_path,
        content_hash=content_hash,
        file_size=file_size,
        mime_type=mime_type,
        document_type=document_type,
        extracted_text=extracted_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"Database: Saved document {document_id} ({filename}) to PostgreSQL")
    return record


def get_document_by_id(db: Session, document_id: str) -> Optional[DocumentRecord]:
    """Retrieve a document by its primary ID."""
    return db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()


def get_document_by_hash(db: Session, content_hash: str) -> Optional[DocumentRecord]:
    """Retrieve an existing document by its content SHA-256 hash (deduplication)."""
    return db.query(DocumentRecord).filter(DocumentRecord.content_hash == content_hash).first()


def list_documents(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    document_type: Optional[str] = None,
) -> List[DocumentRecord]:
    """List documents with pagination and optional type filter."""
    query = db.query(DocumentRecord)
    if document_type:
        query = query.filter(DocumentRecord.document_type == document_type)
    return query.order_by(desc(DocumentRecord.created_at)).offset(offset).limit(limit).all()


def delete_document(db: Session, document_id: str) -> bool:
    """Delete a document and cascade-delete its analysis records."""
    record = get_document_by_id(db, document_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    logger.info(f"Database: Deleted document {document_id}")
    return True


# ---------------------------------------------------------------------------
# 2. Analysis Operations
# ---------------------------------------------------------------------------

def create_analysis(
    db: Session,
    document_id: str,
    document_type: str,
    summary: str,
    completeness_score: float,
    summary_style: str = "detailed",
    analysis_level: str = "standard",
    completeness_breakdown: Optional[List[Dict[str, Any]]] = None,
    extraction_payload: Optional[Dict[str, Any]] = None,
    visual_insights: Optional[Dict[str, Any]] = None,
    uncertainty_flags: Optional[List[str]] = None,
    analysis_id: Optional[str] = None,
) -> AnalysisRecord:
    """Insert an analysis result into PostgreSQL."""
    aid = analysis_id or f"anl-{uuid.uuid4().hex[:12]}"
    record = AnalysisRecord(
        id=aid,
        document_id=document_id,
        document_type=document_type,
        summary_style=summary_style,
        analysis_level=analysis_level,
        summary=summary,
        completeness_score=completeness_score,
        completeness_breakdown=completeness_breakdown or [],
        extraction_payload=extraction_payload or {},
        visual_insights=visual_insights or {},
        uncertainty_flags=uncertainty_flags or [],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"Database: Saved analysis {aid} for document {document_id} to PostgreSQL")
    return record


def get_analysis_by_id(db: Session, analysis_id: str) -> Optional[AnalysisRecord]:
    """Retrieve an analysis record by its ID."""
    return db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()


def get_latest_analysis_for_document(db: Session, document_id: str) -> Optional[AnalysisRecord]:
    """Retrieve the most recent analysis record for a given document."""
    return (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.document_id == document_id)
        .order_by(desc(AnalysisRecord.created_at))
        .first()
    )


def list_analyses_for_document(db: Session, document_id: str) -> List[AnalysisRecord]:
    """List all historical analyses for a document."""
    return (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.document_id == document_id)
        .order_by(desc(AnalysisRecord.created_at))
        .all()
    )
