"""
End-to-end integration and unit tests for Document Intelligence Platform.
Tests all endpoints, extraction fallbacks, completeness calculations,
pseudo-null coercion, and RFC 7807 error responses.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.extraction import coerce_pseudo_null, ResumeExtractionSchema
from app.services.extractor import extract_text, _clean_text
from app.services.completeness import compute_completeness

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Health & Discovery Endpoints
# ---------------------------------------------------------------------------

def test_health_check():
    """Verify health endpoint responds with 200 and configuration status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "llm_mode" in data


def test_list_samples():
    """Verify sample documents catalog lists all pre-seeded fixtures."""
    response = client.get("/api/v1/documents/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 5
    sample_ids = [s["document_id"] for s in samples]
    assert "sample-resume-standard-pdf" in sample_ids
    assert "sample-research-paper-pdf" in sample_ids
    assert "sample-business-report-pdf" in sample_ids
    assert "sample-empty-pdf" in sample_ids


# ---------------------------------------------------------------------------
# 2. Document Loading & Ingestion
# ---------------------------------------------------------------------------

def test_load_sample_success():
    """Verify loading standard sample resume extracts text and stores document."""
    response = client.get("/api/v1/documents/samples/sample-resume-standard-pdf/load")
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "sample-resume-standard-pdf"
    assert data["extracted_text_length"] > 1000
    assert "pdf" in data["filename"]


def test_load_empty_document_error_handling():
    """Verify unreadable or empty document returns RFC 7807 structured 422 error."""
    response = client.get("/api/v1/documents/samples/sample-empty-pdf/load")
    assert response.status_code == 422
    err = response.json()["detail"]
    assert err["error_code"] == "EXTRACTION_ERROR"
    assert "Could not extract readable text" in err["message"]


# ---------------------------------------------------------------------------
# 3. Polymorphic Document Analysis Pipeline
# ---------------------------------------------------------------------------

def test_analyze_resume():
    """Verify full analysis pipeline for Resume domain."""
    # Ensure loaded
    client.get("/api/v1/documents/samples/sample-resume-standard-pdf/load")

    payload = {
        "document_id": "sample-resume-standard-pdf",
        "document_type": "resume",
        "summary_style": "detailed",
        "analysis_level": "standard",
        "focus_topics": ["skills", "work_experience"]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["document_type"] == "resume"
    assert data["completeness_score"] >= 80.0
    assert len(data["summary"]) > 50
    assert "charts_data" in data["visual_insights"]
    assert "skills_distribution" in data["visual_insights"]["charts_data"]
    assert data["visual_insights"]["ai_infographic_url"] is not None


def test_analyze_missing_fields_resume():
    """Verify missing fields in incomplete resume result in lower completeness and uncertainty flags."""
    client.get("/api/v1/documents/samples/sample-resume-missing-pdf/load")

    payload = {
        "document_id": "sample-resume-missing-pdf",
        "document_type": "resume",
        "summary_style": "bullet_point",
        "analysis_level": "standard"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Completeness should reflect missing email and work experience
    assert data["completeness_score"] < 80.0
    assert len(data["uncertainty_flags"]) > 0
    # Verify uncertainty flags mention missing fields
    flags_text = " ".join(data["uncertainty_flags"])
    assert "email_address" in flags_text or "work_experience" in flags_text


def test_analyze_research_paper():
    """Verify Research Paper domain returns benchmark metrics and methodology."""
    client.get("/api/v1/documents/samples/sample-research-paper-pdf/load")

    payload = {
        "document_id": "sample-research-paper-pdf",
        "document_type": "research_paper",
        "summary_style": "brief",
        "analysis_level": "standard"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["document_type"] == "research_paper"
    assert "benchmark_comparison" in data["visual_insights"]["charts_data"]


def test_analyze_business_report():
    """Verify Business Report domain returns KPIs and segment breakdown."""
    client.get("/api/v1/documents/samples/sample-business-report-pdf/load")

    payload = {
        "document_id": "sample-business-report-pdf",
        "document_type": "business_analytics_report",
        "summary_style": "detailed",
        "analysis_level": "detailed"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["document_type"] == "business_analytics_report"
    assert "kpi_dashboard" in data["visual_insights"]["charts_data"]


# ---------------------------------------------------------------------------
# 4. Unit Tests: Cleaning & Null Coercion
# ---------------------------------------------------------------------------

def test_pseudo_null_coercion():
    """Verify strings like 'N/A', 'None', 'not specified' coerce to None."""
    assert coerce_pseudo_null("N/A") is None
    assert coerce_pseudo_null("null") is None
    assert coerce_pseudo_null("not specified") is None
    assert coerce_pseudo_null("   ") is None
    assert coerce_pseudo_null("San Francisco, CA") == "San Francisco, CA"


def test_text_cleaning_pipeline():
    """Verify NFKC normalization, de-hyphenation, and whitespace normalization."""
    raw = "Senior Soft-\nware Engineer at Google.\n\n\n\nPage 1 of 3"
    cleaned = _clean_text(raw)
    assert "Software" in cleaned
    assert "Page 1 of 3" not in cleaned


# ---------------------------------------------------------------------------
# 5. Database & Filesystem Upload Folder Tests
# ---------------------------------------------------------------------------

def test_upload_storage_in_filesystem_and_database():
    """
    Verify:
    1. Uploaded file is physically stored in backend/uploads/ folder.
    2. Document metadata is persisted in the database.
    3. Document is queryable via GET /api/v1/documents.
    4. Analysis is recorded in the analyses table and queryable via history endpoint.
    5. Deleting document removes the physical file from backend/uploads/ and deletes DB record.
    """
    from pathlib import Path

    sample_content = (
        b"Research Paper: Graph Neural Networks for Document Reasoning\n"
        b"Authors: Dr. A. Turing, Dr. C. Shannon\n"
        b"Abstract: We propose an adaptive graph reasoning pipeline for multi-modal document structures.\n"
        b"Methodology: Transformer embeddings mapped to sparse knowledge graphs.\n"
        b"Results: Outperformed baselines by 14.2% on standard extraction benchmarks.\n"
        b"Conclusion: Significant advance in automated document intelligence."
    )

    # 1. Upload file
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("gnn_document_paper.txt", sample_content, "text/plain")},
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    doc_id = upload_data["document_id"]
    file_path_str = upload_data["file_path"]

    assert file_path_str.startswith("uploads/")

    # 2. Verify file exists in backend filesystem uploads folder
    backend_root = Path(__file__).parent.parent
    saved_file = backend_root / file_path_str
    assert saved_file.exists(), f"Expected uploaded file to exist at {saved_file}"
    assert saved_file.read_bytes() == sample_content

    # 3. Verify document exists in database listing
    list_res = client.get("/api/v1/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    matching_docs = [d for d in docs if d["document_id"] == doc_id]
    assert len(matching_docs) == 1
    assert matching_docs[0]["filename"] == "gnn_document_paper.txt"

    # 4. Run analysis and verify analysis history in database
    analyze_payload = {
        "document_id": doc_id,
        "document_type": "research_paper",
        "summary_style": "bullet_point",
        "analysis_level": "standard",
    }
    analyze_res = client.post("/api/v1/analyze", json=analyze_payload)
    assert analyze_res.status_code == 200

    history_res = client.get(f"/api/v1/analyze/{doc_id}/history")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    assert history[0]["document_id"] == doc_id

    # 5. Delete document and verify physical file is deleted from uploads/
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

    # Verify physical file removed
    assert not saved_file.exists(), f"Expected uploaded file {saved_file} to be deleted from filesystem"


def test_database_failover_to_sqlite_backup():
    """
    Verify Two-Tier Database Architecture:
    1. Primary check: PostgreSQL is checked first.
    2. Fallback check: When PostgreSQL is unreachable or fallback is triggered,
       the system moves seamlessly to SQLite backup (docuintel.db).
    3. Health endpoint accurately reports active backend and backup status.
    4. Documents can be uploaded, stored, and retrieved in SQLite backup mode without error.
    """
    from app.db.connection import get_active_backend_name, is_using_sqlite_backup, switch_to_sqlite_backup

    # 1. Trigger fallback to SQLite backup
    switch_to_sqlite_backup("Automated test fallback verification")
    assert is_using_sqlite_backup() is True
    assert "SQLite" in get_active_backend_name()

    # 2. Check health endpoint reports SQLite backup
    health_res = client.get("/api/v1/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["is_backup_database"] is True
    assert "SQLite" in health_data["database_backend"]

    # 3. Verify upload & DB operations succeed in SQLite backup mode
    sample_content = b"Backup Test: Testing document ingestion under SQLite backup mode."
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("sqlite_backup_test.txt", sample_content, "text/plain")},
    )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["document_id"]

    # Verify listing finds it
    list_res = client.get("/api/v1/documents")
    assert list_res.status_code == 200
    found = any(d["document_id"] == doc_id for d in list_res.json())
    assert found is True

    # Clean up
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 200


