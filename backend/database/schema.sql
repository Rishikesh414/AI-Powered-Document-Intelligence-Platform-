-- ============================================================================
-- DocuIntel AI — PostgreSQL Database Schema
-- Run this script in pgAdmin, DBeaver, psql, or Supabase SQL Editor.
-- ============================================================================

-- 1. Documents Table
-- Stores document metadata, extracted text, and backend filesystem path.
-- Actual binary files (PDF, TXT, DOCX) are stored in the backend filesystem folder: 'backend/uploads/'.
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(64) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,            -- Local backend filesystem storage path
    content_hash VARCHAR(64) NOT NULL,           -- SHA-256 hash of extracted text for idempotency
    file_size INTEGER NOT NULL DEFAULT 0,        -- Size in bytes
    mime_type VARCHAR(128) NOT NULL DEFAULT 'application/pdf',
    document_type VARCHAR(64),                   -- resume | research_paper | business_analytics_report
    extracted_text TEXT NOT NULL,                -- Extracted clean text content
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc') NOT NULL
);

-- Index on content_hash for fast deduplication checks
CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents (content_hash);
-- Index on document_type for filtering
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents (document_type);
-- Index on created_at for chronological ordering
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents (created_at DESC);

COMMENT ON TABLE documents IS 'Metadata and extracted text for processed documents; binary files stored in backend uploads/';
COMMENT ON COLUMN documents.file_path IS 'Path to the physical file stored in the backend uploads/ filesystem directory';


-- 2. Analyses Table
-- Stores AI analysis results, summaries, completeness scores, and visual insights.
CREATE TABLE IF NOT EXISTS analyses (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    document_type VARCHAR(64) NOT NULL,          -- resume | research_paper | business_analytics_report
    summary_style VARCHAR(32) NOT NULL DEFAULT 'detailed',    -- brief | detailed | bullet_point
    analysis_level VARCHAR(32) NOT NULL DEFAULT 'standard',   -- basic | standard | detailed
    summary TEXT NOT NULL,                       -- AI-generated summary text
    completeness_score DOUBLE PRECISION NOT NULL DEFAULT 0.0, -- 0 to 100%
    completeness_breakdown JSONB,                -- Dimension-by-dimension weighted scores
    extraction_payload JSONB,                    -- Structured Pydantic extraction schema payload
    visual_insights JSONB,                       -- Chart data series and infographic URL
    uncertainty_flags JSONB,                     -- Detected missing or low-confidence fields
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc') NOT NULL
);

-- Index on document_id for fast lookup of analyses per document
CREATE INDEX IF NOT EXISTS idx_analyses_document_id ON analyses (document_id);
-- Index on created_at for retrieving the latest analysis
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses (created_at DESC);

COMMENT ON TABLE analyses IS 'AI analysis results, polymorphic extractions, summaries, and completeness scores';


-- ============================================================================
-- 3. Useful Queries / Verification
-- ============================================================================

-- List all uploaded documents with analysis counts
-- SELECT d.id, d.filename, d.document_type, d.file_size, COUNT(a.id) AS total_analyses, d.created_at
-- FROM documents d
-- LEFT JOIN analyses a ON d.id = a.document_id
-- GROUP BY d.id
-- ORDER BY d.created_at DESC;

-- Get latest analysis for a document
-- SELECT a.id, a.document_id, a.completeness_score, a.summary_style, a.created_at
-- FROM analyses a
-- WHERE a.document_id = 'your-document-id'
-- ORDER BY a.created_at DESC
-- LIMIT 1;
