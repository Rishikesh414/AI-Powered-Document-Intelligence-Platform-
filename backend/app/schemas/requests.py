"""
Request and response models for the API layer.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    """Request body for POST /api/v1/analyze."""
    document_id: str
    document_type: Literal["resume", "research_paper", "business_analytics_report"]
    summary_style: Literal["brief", "detailed", "bullet_point"] = "detailed"
    analysis_level: Literal["basic", "standard", "detailed"] = "standard"
    focus_topics: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class CompletenessBreakdown(BaseModel):
    """Per-dimension completeness breakdown."""
    dimension: str
    label: str
    weight: float
    score: float


class VisualInsights(BaseModel):
    """Visual insights data for the frontend."""
    charts_data: Dict[str, Any] = Field(default_factory=dict)
    ai_infographic_url: Optional[str] = None  # Deprecated (Pollinations.ai broke)
    ai_infographic_svg: Optional[str] = None  # Server-generated SVG content
    generation_method: Optional[str] = None   # "server_svg" | legacy "pollinations"



class AnalyzeResponse(BaseModel):
    """Response body for POST /api/v1/analyze."""
    document_id: str
    document_type: str
    summary: str
    extraction: Dict[str, Any]
    completeness_score: float
    completeness_breakdown: List[CompletenessBreakdown]
    uncertainty_flags: List[str]
    visual_insights: VisualInsights
    analysis_level: str
    summary_style: str


class DocumentInfo(BaseModel):
    """Metadata about an uploaded or sample document."""
    document_id: str
    filename: str
    file_path: Optional[str] = None
    title: Optional[str] = None
    document_type: Optional[str] = None
    size_bytes: int = 0
    is_sample: bool = False
    description: Optional[str] = None


class UploadResponse(BaseModel):
    """Response body for POST /api/v1/documents/upload."""
    document_id: str
    filename: str
    file_path: Optional[str] = None
    size_bytes: int
    extracted_text_length: int
    message: str


class ErrorResponse(BaseModel):
    """RFC 7807-inspired structured error response."""
    error_code: str
    message: str
    remediation: Optional[str] = None
