"""
Polymorphic Pydantic v2 extraction schemas for all 3 document types.
Implements pseudo-null coercion, evidence tracking, and structured validation.
"""

from __future__ import annotations

import re
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Utility: Pseudo-Null Coercion
# ---------------------------------------------------------------------------

_PSEUDO_NULLS = {
    "n/a", "na", "none", "null", "unknown", "not specified",
    "not available", "not provided", "not found", "not applicable",
    "-", "—", "–", "", "unspecified",
}


def coerce_pseudo_null(v: Optional[str]) -> Optional[str]:
    """Convert LLM-generated placeholder strings to proper Python None."""
    if v is None:
        return None
    if isinstance(v, str) and v.strip().lower() in _PSEUDO_NULLS:
        return None
    return v.strip() if isinstance(v, str) else v


# ---------------------------------------------------------------------------
# Shared Sub-Models
# ---------------------------------------------------------------------------

class EducationItem(BaseModel):
    """A single educational qualification entry."""
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    gpa: Optional[str] = None

    @field_validator("degree", "field_of_study", "institution", "start_year", "end_year", "gpa", mode="before")
    @classmethod
    def clean(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)


class WorkExperienceItem(BaseModel):
    """A single work experience entry."""
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)

    @field_validator("job_title", "company", "location", "start_date", "end_date", "description", mode="before")
    @classmethod
    def clean(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)


class SkillCategory(BaseModel):
    """Skills grouped by category."""
    category: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class BenchmarkMetricItem(BaseModel):
    """A single benchmark result from a research paper."""
    metric_name: Optional[str] = None
    dataset: Optional[str] = None
    proposed_value: Optional[str] = None
    baseline_value: Optional[str] = None
    unit: Optional[str] = None

    @field_validator("metric_name", "dataset", "proposed_value", "baseline_value", "unit", mode="before")
    @classmethod
    def clean(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)


class ExecutiveKPIItem(BaseModel):
    """A single KPI from a business analytics report."""
    kpi_name: Optional[str] = None
    actual_value: Optional[str] = None
    target_or_prior_value: Optional[str] = None
    unit: Optional[str] = None
    change_percentage: Optional[str] = None
    status: Optional[str] = None

    @field_validator("kpi_name", "actual_value", "target_or_prior_value", "unit", "change_percentage", "status", mode="before")
    @classmethod
    def clean(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)


class SegmentPerformanceItem(BaseModel):
    """A single segment performance entry from a business report."""
    segment_name: Optional[str] = None
    revenue_or_metric_value: Optional[str] = None
    share_percentage: Optional[str] = None
    growth_rate_pct: Optional[str] = None

    @field_validator("segment_name", "revenue_or_metric_value", "share_percentage", "growth_rate_pct", mode="before")
    @classmethod
    def clean(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)


# ---------------------------------------------------------------------------
# 1. RESUME EXTRACTION SCHEMA
# ---------------------------------------------------------------------------

class ResumeExtractionSchema(BaseModel):
    """Structured extraction schema for resume/CV documents."""
    document_type: Literal["resume"] = "resume"
    candidate_name: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    professional_summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    categorized_skills: List[SkillCategory] = Field(default_factory=list)
    educational_qualifications: List[EducationItem] = Field(default_factory=list)
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    summary: str = ""
    uncertainty_flags: List[str] = Field(default_factory=list)

    @field_validator(
        "candidate_name", "email_address", "phone_number",
        "location", "linkedin_url", "professional_summary",
        mode="before",
    )
    @classmethod
    def clean_scalars(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)

    @field_validator(
        "skills", "categorized_skills", "educational_qualifications",
        "work_experience", "certifications", "languages", "uncertainty_flags",
        mode="before",
    )
    @classmethod
    def clean_lists(cls, v: Any) -> Any:
        return [] if v is None else v


# ---------------------------------------------------------------------------
# 2. RESEARCH PAPER EXTRACTION SCHEMA
# ---------------------------------------------------------------------------

class ResearchPaperExtractionSchema(BaseModel):
    """Structured extraction schema for academic/research papers."""
    document_type: Literal["research_paper"] = "research_paper"
    paper_title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    publication_venue: Optional[str] = None
    publication_year: Optional[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    research_objective: Optional[str] = None
    methodology_summary: Optional[str] = None
    datasets_used: List[str] = Field(default_factory=list)
    benchmark_results: List[BenchmarkMetricItem] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    limitations_and_future_work: Optional[str] = None
    references_count: Optional[int] = None
    summary: str = ""
    uncertainty_flags: List[str] = Field(default_factory=list)

    @field_validator(
        "paper_title", "publication_venue", "publication_year",
        "abstract", "research_objective", "methodology_summary",
        "limitations_and_future_work",
        mode="before",
    )
    @classmethod
    def clean_scalars(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)

    @field_validator(
        "authors", "keywords", "datasets_used", "benchmark_results",
        "key_findings", "uncertainty_flags",
        mode="before",
    )
    @classmethod
    def clean_lists(cls, v: Any) -> Any:
        return [] if v is None else v


# ---------------------------------------------------------------------------
# 3. BUSINESS ANALYTICS REPORT EXTRACTION SCHEMA
# ---------------------------------------------------------------------------

class BusinessReportExtractionSchema(BaseModel):
    """Structured extraction schema for business analytics reports."""
    document_type: Literal["business_analytics_report"] = "business_analytics_report"
    report_title: Optional[str] = None
    company_name: Optional[str] = None
    reporting_period: Optional[str] = None
    executive_summary: Optional[str] = None
    executive_kpis: List[ExecutiveKPIItem] = Field(default_factory=list)
    segment_breakdown: List[SegmentPerformanceItem] = Field(default_factory=list)
    key_growth_drivers: List[str] = Field(default_factory=list)
    risk_factors_and_anomalies: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)
    summary: str = ""
    uncertainty_flags: List[str] = Field(default_factory=list)

    @field_validator(
        "report_title", "company_name", "reporting_period", "executive_summary",
        mode="before",
    )
    @classmethod
    def clean_scalars(cls, v: Optional[str]) -> Optional[str]:
        return coerce_pseudo_null(v)

    @field_validator(
        "executive_kpis", "segment_breakdown", "key_growth_drivers",
        "risk_factors_and_anomalies", "strategic_recommendations", "uncertainty_flags",
        mode="before",
    )
    @classmethod
    def clean_lists(cls, v: Any) -> Any:
        return [] if v is None else v


# ---------------------------------------------------------------------------
# Polymorphic Union Type
# ---------------------------------------------------------------------------

DocumentExtractionPayload = Union[
    ResumeExtractionSchema,
    ResearchPaperExtractionSchema,
    BusinessReportExtractionSchema,
]


def get_schema_class(document_type: str) -> type[BaseModel]:
    """Return the appropriate schema class for a given document type."""
    mapping = {
        "resume": ResumeExtractionSchema,
        "research_paper": ResearchPaperExtractionSchema,
        "business_analytics_report": BusinessReportExtractionSchema,
    }
    if document_type not in mapping:
        raise ValueError(f"Unknown document type: {document_type}. Must be one of {list(mapping.keys())}")
    return mapping[document_type]
