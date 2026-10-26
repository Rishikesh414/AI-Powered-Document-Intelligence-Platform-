"""
Weighted Multi-Dimensional Completeness & Certainty Scoring Engine.
Computes C_total (0–100%) for each document type based on Doc 2's formula.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.schemas.requests import CompletenessBreakdown


# ---------------------------------------------------------------------------
# Per-Document-Type Validation Dimensions & Weights
# ---------------------------------------------------------------------------

RESUME_DIMENSIONS: List[Tuple[str, str, float, List[str]]] = [
    ("identity", "Identity (Name)", 0.20, ["candidate_name"]),
    ("contactability", "Contactability (Email, Phone)", 0.15, ["email_address", "phone_number"]),
    ("competency", "Competency Matrix (Skills)", 0.25, ["skills", "categorized_skills"]),
    ("education", "Academic Pedigree (Education)", 0.15, ["educational_qualifications"]),
    ("experience", "Work Track Record (Experience)", 0.25, ["work_experience"]),
]

RESEARCH_PAPER_DIMENSIONS: List[Tuple[str, str, float, List[str]]] = [
    ("bibliographic", "Bibliographic Identity (Title, Authors)", 0.20, ["paper_title", "authors"]),
    ("objective", "Problem & Objective", 0.15, ["research_objective"]),
    ("methodology", "Methodology & Datasets", 0.25, ["methodology_summary", "datasets_used"]),
    ("benchmarks", "Empirical Benchmarks", 0.20, ["benchmark_results"]),
    ("findings", "Findings & Limitations", 0.20, ["key_findings", "limitations_and_future_work"]),
]

BUSINESS_REPORT_DIMENSIONS: List[Tuple[str, str, float, List[str]]] = [
    ("metadata", "Report Metadata (Title, Period)", 0.15, ["report_title", "reporting_period"]),
    ("kpis", "Executive KPIs", 0.30, ["executive_kpis"]),
    ("segments", "Segment Breakdown", 0.20, ["segment_breakdown"]),
    ("drivers", "Drivers & Anomalies", 0.15, ["key_growth_drivers", "risk_factors_and_anomalies"]),
    ("strategy", "Strategic Recommendations", 0.20, ["strategic_recommendations"]),
]

_DIMENSION_MAP = {
    "resume": RESUME_DIMENSIONS,
    "research_paper": RESEARCH_PAPER_DIMENSIONS,
    "business_analytics_report": BUSINESS_REPORT_DIMENSIONS,
}


def _field_completeness(extraction: Dict[str, Any], field_name: str) -> float:
    """
    Score a single field's completeness (0.0 to 1.0).
    - None/null → 0.0
    - Empty list/string → 0.0
    - Non-empty string → 1.0
    - Non-empty list → min(1.0, len/expected)
    - List of objects → score based on non-null child attributes
    """
    value = extraction.get(field_name)

    if value is None:
        return 0.0

    if isinstance(value, str):
        return 1.0 if value.strip() else 0.0

    if isinstance(value, list):
        if len(value) == 0:
            return 0.0

        # For list of strings
        if all(isinstance(v, str) for v in value):
            return 1.0

        # For list of dicts (sub-models)
        if all(isinstance(v, dict) for v in value):
            total_children = 0
            filled_children = 0
            for item in value:
                for k, v in item.items():
                    if k in ("document_type",):
                        continue
                    total_children += 1
                    if v is not None and v != "" and v != []:
                        filled_children += 1
            return filled_children / total_children if total_children > 0 else 0.5

        return 1.0

    if isinstance(value, (int, float)):
        return 1.0

    return 0.0


def compute_completeness(
    extraction: Dict[str, Any],
    document_type: str,
) -> Tuple[float, List[CompletenessBreakdown]]:
    """
    Compute the Weighted Multi-Dimensional Completeness Score.

    Returns:
        (c_total, breakdown) where c_total is 0–100 and breakdown
        is a list of per-dimension scores.
    """
    dimensions = _DIMENSION_MAP.get(document_type, RESUME_DIMENSIONS)
    breakdown: List[CompletenessBreakdown] = []
    c_total = 0.0

    for dim_id, dim_label, weight, fields in dimensions:
        # Average completeness across the fields in this dimension
        if fields:
            field_scores = [_field_completeness(extraction, f) for f in fields]
            dim_score = sum(field_scores) / len(field_scores)
        else:
            dim_score = 0.0

        weighted = dim_score * weight
        c_total += weighted

        breakdown.append(CompletenessBreakdown(
            dimension=dim_id,
            label=dim_label,
            weight=weight,
            score=round(dim_score * 100, 1),
        ))

    # Scale to 0–100
    c_total_pct = round(c_total * 100, 1)
    return c_total_pct, breakdown
