"""
Multi-stage document text extraction service.
Pipeline: pdfplumber → PyMuPDF → raw text fallback.
Handles PDF, TXT, and DOCX formats with NFKC normalization and cleaning.
"""

from __future__ import annotations

import hashlib
import io
import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of cleaned text for idempotency."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clean_text(raw: str) -> str:
    """
    Apply deterministic text cleaning:
    1. NFKC Unicode normalization (ligatures → standard chars)
    2. De-hyphenation across line breaks
    3. Whitespace collapse (preserve paragraph breaks)
    4. Strip common headers/footers/watermarks
    """
    # NFKC normalization
    text = unicodedata.normalize("NFKC", raw)

    # Remove non-printable control characters (keep newlines, tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # De-hyphenation: rejoin words split across lines
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # Strip common header/footer patterns
    text = re.sub(r"(?i)^(page\s+\d+\s*(of\s+\d+)?|confidential|draft)\s*$", "", text, flags=re.MULTILINE)

    # Collapse excessive whitespace while preserving paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_from_pdf_pdfplumber(file_bytes: bytes) -> Optional[str]:
    """
    Extract text from PDF using pdfplumber.
    Handles multi-column layouts by using spatial sorting.
    """
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(
                    x_tolerance=3,
                    y_tolerance=3,
                )
                if page_text:
                    text_parts.append(page_text)

                # Also try extracting tables
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        for row in table:
                            if row:
                                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                                text_parts.append(" | ".join(cleaned_row))

        combined = "\n\n".join(text_parts)
        if combined.strip():
            return combined
        return None

    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")
        return None


def extract_from_pdf_pymupdf(file_bytes: bytes) -> Optional[str]:
    """
    Fallback PDF extraction using PyMuPDF (fitz).
    Uses block-level extraction for better layout handling.
    """
    try:
        import pymupdf

        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        text_parts = []

        for page in doc:
            blocks = page.get_text("blocks")
            # Sort blocks by vertical position, then horizontal
            blocks.sort(key=lambda b: (b[1], b[0]))
            for block in blocks:
                block_text = block[4].strip()
                if block_text:
                    text_parts.append(block_text)

        doc.close()
        combined = "\n\n".join(text_parts)
        if combined.strip():
            return combined
        return None

    except Exception as e:
        logger.warning(f"PyMuPDF extraction failed: {e}")
        return None


def extract_from_txt(file_bytes: bytes) -> Optional[str]:
    """Extract text from plain text files."""
    try:
        # Try UTF-8 first, then latin-1 as fallback
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                text = file_bytes.decode(encoding)
                if text.strip():
                    return text
            except (UnicodeDecodeError, UnicodeError):
                continue
        return None
    except Exception as e:
        logger.warning(f"Text extraction failed: {e}")
        return None


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Main extraction entry point.
    Determines file type and applies the appropriate extraction pipeline.

    Returns cleaned text or raises ValueError if extraction fails.
    """
    if len(file_bytes) == 0:
        raise ValueError("EMPTY_DOCUMENT: Uploaded file contains 0 bytes of readable content.")

    ext = Path(filename).suffix.lower()
    text = None

    if ext == ".pdf":
        # Stage 1: Try pdfplumber (best for structured PDFs)
        text = extract_from_pdf_pdfplumber(file_bytes)

        # Stage 2: Fallback to PyMuPDF
        if not text:
            logger.info("pdfplumber returned empty, falling back to PyMuPDF")
            text = extract_from_pdf_pymupdf(file_bytes)

    elif ext in (".txt", ".text", ".md"):
        text = extract_from_txt(file_bytes)

    elif ext == ".docx":
        # Basic DOCX support via python-docx if available
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n\n".join(paragraphs)
        except ImportError:
            raise ValueError("UNSUPPORTED_FORMAT: DOCX support requires python-docx library.")
        except Exception as e:
            logger.warning(f"DOCX extraction failed: {e}")
            text = None
    else:
        raise ValueError(
            f"UNSUPPORTED_FORMAT: File extension '{ext}' is not supported. "
            "Upload a PDF, TXT, or DOCX file."
        )

    if not text or not text.strip():
        raise ValueError(
            "UNREADABLE_CONTENT: Could not extract readable text from the document. "
            "The file may be a scanned image without OCR text, corrupted, or empty."
        )

    # Apply cleaning pipeline
    cleaned = _clean_text(text)

    if not cleaned:
        raise ValueError(
            "UNREADABLE_CONTENT: Document text was empty after cleaning. "
            "Upload a document with readable text content."
        )

    return cleaned
