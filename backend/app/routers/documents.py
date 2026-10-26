"""
Document management routes: upload, sample document endpoints, and PostgreSQL operations.
Persists uploaded binary files to the backend filesystem upload folder ('backend/uploads/').
Stores metadata and extracted text in PostgreSQL database.
"""

from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.db import crud, get_db, DocumentRecord
from app.schemas.requests import DocumentInfo, UploadResponse
from app.services.extractor import compute_content_hash, extract_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])

# ---------------------------------------------------------------------------
# Storage paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
UPLOADS_DIR = BASE_DIR / settings.UPLOAD_DIR

# Ensure backend upload folder exists
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# In-memory hot cache for zero-latency retrieval
_document_store: Dict[str, Dict] = {}


# Pre-seeded sample fixtures catalog
SAMPLE_DOCUMENTS = [
    {
        "id": "sample-resume-standard-pdf",
        "filename": "sample_resume_standard.pdf",
        "document_type": "resume",
        "title": "Sarah Chen - Senior Full-Stack Engineer (PDF)",
        "description": "Comprehensive resume with full contact info, skills matrix, education, and career track record.",
    },
    {
        "id": "sample-resume-standard-txt",
        "filename": "sample_resume_standard.txt",
        "document_type": "resume",
        "title": "Sarah Chen - Senior Full-Stack Engineer (TXT)",
        "description": "Standard plain text resume for testing raw text extraction and structured parsing.",
    },
    {
        "id": "sample-resume-missing-pdf",
        "filename": "sample_resume_missing_fields.pdf",
        "document_type": "resume",
        "title": "Alex Rivera - Incomplete Resume (PDF)",
        "description": "Entry-level candidate missing email, phone, location, and work experience to test null handling.",
    },
    {
        "id": "sample-research-paper-pdf",
        "filename": "sample_research_paper.pdf",
        "document_type": "research_paper",
        "title": "Adaptive RAG for Document Understanding (PDF)",
        "description": "Academic AI paper with abstract, methodology, benchmark tables, and future directions.",
    },
    {
        "id": "sample-business-report-pdf",
        "filename": "sample_business_report.pdf",
        "document_type": "business_analytics_report",
        "title": "Acme Corp Q3 2024 Financial Analytics (PDF)",
        "description": "Executive business report with KPIs, segment revenues, growth drivers, and strategic recommendations.",
    },
    {
        "id": "sample-empty-pdf",
        "filename": "sample_empty.pdf",
        "document_type": None,
        "title": "Empty / Blank Document (PDF)",
        "description": "Blank PDF fixture to test graceful error handling and remediation suggestions.",
    },
]


def get_document_store() -> Dict[str, Dict]:
    """Access the in-memory document hot cache."""
    return _document_store


def get_document_data(doc_id: str, db: Optional[Session] = None) -> Optional[Dict]:
    """
    Retrieve document data first from in-memory hot cache,
    falling back to PostgreSQL database if cache misses (e.g. after server restart).
    """
    if doc_id in _document_store:
        return _document_store[doc_id]

    if db:
        record = crud.get_document_by_id(db, doc_id)
        if record:
            data = {
                "id": record.id,
                "filename": record.filename,
                "file_path": record.file_path,
                "text": record.extracted_text,
                "content_hash": record.content_hash,
                "size_bytes": record.file_size,
                "document_type": record.document_type,
            }
            _document_store[doc_id] = data
            return data

    return None


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document (PDF, TXT, DOCX) for processing:
    1. Validates MIME type and 10MB size limit.
    2. Extracts clean text via multi-stage pipeline.
    3. Saves binary file to the backend filesystem upload folder ('backend/uploads/').
    4. Persists metadata and extracted text to PostgreSQL.
    """
    # 1. Validate filename
    if not file.filename:
        raise HTTPException(status_code=422, detail={
            "error_code": "INVALID_FILENAME",
            "message": "No filename provided.",
            "remediation": "Upload a file with a valid filename.",
        })

    # 2. Validate extension
    ext = Path(file.filename).suffix.lower()
    allowed = {".pdf", ".txt", ".text", ".md", ".docx"}
    if ext not in allowed:
        raise HTTPException(status_code=415, detail={
            "error_code": "UNSUPPORTED_FORMAT",
            "message": f"File type '{ext}' is not supported.",
            "remediation": f"Upload a file with one of these extensions: {', '.join(allowed)}",
        })

    # 3. Read file bytes
    file_bytes = await file.read()

    # 4. Validate size (max 10MB)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=413, detail={
            "error_code": "FILE_TOO_LARGE",
            "message": f"File size ({len(file_bytes)} bytes) exceeds maximum ({max_bytes} bytes).",
            "remediation": "Upload a file smaller than 10MB.",
        })

    # 5. Extract text
    try:
        extracted_text = extract_text(file_bytes, file.filename)
    except ValueError as e:
        error_msg = str(e)
        error_code = "EXTRACTION_ERROR"
        if "EMPTY_DOCUMENT" in error_msg:
            error_code = "EMPTY_DOCUMENT"
        elif "UNSUPPORTED_FORMAT" in error_msg:
            error_code = "UNSUPPORTED_FORMAT"
        elif "UNREADABLE_CONTENT" in error_msg:
            error_code = "UNREADABLE_CONTENT"

        raise HTTPException(status_code=422, detail={
            "error_code": error_code,
            "message": error_msg.split(": ", 1)[-1] if ": " in error_msg else error_msg,
            "remediation": "Upload a valid PDF, TXT, or DOCX file with readable content.",
        })

    # 6. Generate document ID
    doc_id = f"doc-{uuid.uuid4().hex[:12]}"
    clean_filename = re.sub(r"[^\w\.-]", "_", file.filename)
    saved_filename = f"{doc_id}_{clean_filename}"
    saved_file_path = UPLOADS_DIR / saved_filename

    # 7. Save file to backend filesystem upload directory
    try:
        saved_file_path.write_bytes(file_bytes)
        rel_file_path = f"uploads/{saved_filename}"
        logger.info(f"Filesystem: Saved uploaded file to {saved_file_path}")
    except Exception as e:
        logger.error(f"Failed to save file to filesystem: {e}")
        rel_file_path = str(saved_file_path)

    # 8. Compute content hash
    content_hash = compute_content_hash(extracted_text)

    # 9. Store in PostgreSQL database
    try:
        crud.create_document(
            db=db,
            document_id=doc_id,
            filename=file.filename,
            file_path=rel_file_path,
            content_hash=content_hash,
            file_size=len(file_bytes),
            extracted_text=extracted_text,
            mime_type=file.content_type or ("application/pdf" if ext == ".pdf" else "text/plain"),
        )
    except Exception as e:
        logger.warning(f"Could not persist to database (continuing with hot cache): {e}")

    # 10. Update hot cache
    _document_store[doc_id] = {
        "id": doc_id,
        "filename": file.filename,
        "file_path": rel_file_path,
        "text": extracted_text,
        "content_hash": content_hash,
        "size_bytes": len(file_bytes),
    }

    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
        file_path=rel_file_path,
        size_bytes=len(file_bytes),
        extracted_text_length=len(extracted_text),
        message="Document uploaded, stored in uploads/ folder, and indexed in PostgreSQL successfully.",
    )


@router.get("/documents", response_model=List[DocumentInfo])
async def list_stored_documents(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List all documents currently stored in the PostgreSQL database."""
    try:
        records = crud.list_documents(db=db, limit=limit, offset=offset)
        return [
            DocumentInfo(
                document_id=r.id,
                filename=r.filename,
                file_path=r.file_path,
                document_type=r.document_type,
                size_bytes=r.file_size,
                is_sample=False,
                description=f"Stored in {r.file_path}",
            )
            for r in records
        ]
    except Exception as e:
        logger.warning(f"Error reading documents from database: {e}")
        # Fallback to in-memory store
        return [
            DocumentInfo(
                document_id=d["id"],
                filename=d["filename"],
                file_path=d.get("file_path"),
                size_bytes=d.get("size_bytes", 0),
                is_sample=False,
            )
            for d in _document_store.values()
        ]


@router.get("/documents/samples", response_model=List[DocumentInfo])
async def list_samples():
    """List all available pre-seeded sample documents for testing."""
    results = []
    for sample in SAMPLE_DOCUMENTS:
        file_path = SAMPLES_DIR / sample["filename"]
        size = file_path.stat().st_size if file_path.exists() else 0
        results.append(DocumentInfo(
            document_id=sample["id"],
            filename=sample["filename"],
            file_path=f"samples/{sample['filename']}",
            title=sample.get("title"),
            document_type=sample.get("document_type"),
            size_bytes=size,
            is_sample=True,
            description=sample.get("description"),
        ))
    return results


@router.get("/documents/samples/{sample_id}/load", response_model=UploadResponse)
async def load_sample(
    sample_id: str,
    db: Session = Depends(get_db),
):
    """Load a sample document into memory and index it in the PostgreSQL database."""
    sample = next((s for s in SAMPLE_DOCUMENTS if s["id"] == sample_id), None)
    if not sample:
        raise HTTPException(status_code=404, detail={
            "error_code": "SAMPLE_NOT_FOUND",
            "message": f"Sample '{sample_id}' not found.",
            "remediation": "Use GET /api/v1/documents/samples to list available samples.",
        })

    file_path = SAMPLES_DIR / sample["filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail={
            "error_code": "SAMPLE_FILE_MISSING",
            "message": f"Sample file '{sample['filename']}' not found on disk.",
        })

    file_bytes = file_path.read_bytes()

    try:
        extracted_text = extract_text(file_bytes, sample["filename"])
    except ValueError as e:
        raise HTTPException(status_code=422, detail={
            "error_code": "EXTRACTION_ERROR",
            "message": str(e),
        })

    content_hash = compute_content_hash(extracted_text)
    rel_path = f"samples/{sample['filename']}"

    # Index in PostgreSQL
    try:
        crud.create_document(
            db=db,
            document_id=sample_id,
            filename=sample["filename"],
            file_path=rel_path,
            content_hash=content_hash,
            file_size=len(file_bytes),
            extracted_text=extracted_text,
            mime_type="application/pdf" if sample["filename"].endswith(".pdf") else "text/plain",
            document_type=sample.get("document_type"),
        )
    except Exception as e:
        # Ignore duplicate key error if already indexed
        db.rollback()
        pass

    # Update in-memory hot cache
    _document_store[sample_id] = {
        "id": sample_id,
        "filename": sample["filename"],
        "file_path": rel_path,
        "text": extracted_text,
        "content_hash": content_hash,
        "size_bytes": len(file_bytes),
        "document_type": sample.get("document_type"),
    }

    return UploadResponse(
        document_id=sample_id,
        filename=sample["filename"],
        file_path=rel_path,
        size_bytes=len(file_bytes),
        extracted_text_length=len(extracted_text),
        message=f"Sample document '{sample['filename']}' loaded successfully.",
    )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Delete a document record from PostgreSQL and remove its file from uploads/."""
    # Check in-memory store
    doc = _document_store.pop(document_id, None)

    # Determine file path to clean up from filesystem
    file_path = doc.get("file_path") if doc else None
    if not file_path:
        existing_record = crud.get_document_by_id(db, document_id)
        if existing_record:
            file_path = existing_record.file_path

    # Delete from PostgreSQL
    deleted = crud.delete_document(db=db, document_id=document_id)

    # Remove file from filesystem if it exists in uploads/
    if file_path:
        fpath = BASE_DIR / file_path
        if fpath.exists() and "uploads" in str(fpath):
            try:
                fpath.unlink()
                logger.info(f"Filesystem: Removed {fpath}")
            except Exception as e:
                logger.warning(f"Failed to remove file from filesystem: {e}")

    if not deleted and not doc:
        raise HTTPException(status_code=404, detail={"message": f"Document '{document_id}' not found."})

    return {"status": "deleted", "document_id": document_id}
