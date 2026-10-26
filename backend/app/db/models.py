"""
SQLAlchemy ORM models for PostgreSQL database.
Defines DocumentRecord and AnalysisRecord tables with foreign keys and indexes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.db.connection import Base


class DocumentRecord(Base):
    """
    Metadata and extracted content for documents stored in the system.
    Actual binary files are persisted in the backend filesystem upload directory.
    """
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)  # Local filesystem path (e.g. uploads/doc-xxx_resume.pdf)
    content_hash = Column(String(64), nullable=False, index=True)  # SHA-256 for idempotency
    file_size = Column(Integer, nullable=False, default=0)
    mime_type = Column(String(128), nullable=False, default="application/pdf")
    document_type = Column(String(64), nullable=True)  # resume | research_paper | business_analytics_report
    extracted_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analyses = relationship(
        "AnalysisRecord",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="desc(AnalysisRecord.created_at)"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "document_id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "size_bytes": self.file_size,
            "mime_type": self.mime_type,
            "document_type": self.document_type,
            "extracted_text_length": len(self.extracted_text) if self.extracted_text else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AnalysisRecord(Base):
    """
    Persisted AI analysis results, summaries, structured extractions, and completeness scores.
    """
    __tablename__ = "analyses"

    id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String(64), nullable=False)
    summary_style = Column(String(32), nullable=False, default="detailed")
    analysis_level = Column(String(32), nullable=False, default="standard")
    summary = Column(Text, nullable=False)
    completeness_score = Column(Float, nullable=False, default=0.0)

    # JSON payloads (compatible with PostgreSQL JSON/JSONB and SQLite JSON)
    completeness_breakdown = Column(JSON, nullable=True)
    extraction_payload = Column(JSON, nullable=True)
    visual_insights = Column(JSON, nullable=True)
    uncertainty_flags = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    document = relationship("DocumentRecord", back_populates="analyses")

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "summary_style": self.summary_style,
            "analysis_level": self.analysis_level,
            "summary": self.summary,
            "completeness_score": self.completeness_score,
            "completeness_breakdown": self.completeness_breakdown or [],
            "extraction": self.extraction_payload or {},
            "visual_insights": self.visual_insights or {},
            "uncertainty_flags": self.uncertainty_flags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
