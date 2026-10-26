"""
Visual insights service.
- Generates chart data for ECharts (frontend)
- Generates AI infographic URL via Pollinations.ai
"""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List, Optional

from app.config import settings


def _build_resume_charts(extraction: Dict[str, Any]) -> Dict[str, Any]:
    """Build ECharts-ready data for resume documents."""
    charts: Dict[str, Any] = {}

    # 1. Skills Distribution (pie/bar chart)
    categorized = extraction.get("categorized_skills", [])
    if categorized:
        categories = []
        counts = []
        for cat in categorized:
            cat_name = cat.get("category", "Other") if isinstance(cat, dict) else "Other"
            cat_skills = cat.get("skills", []) if isinstance(cat, dict) else []
            categories.append(cat_name)
            counts.append(len(cat_skills))

        charts["skills_distribution"] = {
            "type": "pie",
            "title": "Skills Distribution by Category",
            "data": [{"name": c, "value": v} for c, v in zip(categories, counts)],
        }
    elif extraction.get("skills"):
        skills = extraction["skills"][:15]
        charts["skills_distribution"] = {
            "type": "bar",
            "title": "Key Skills",
            "categories": skills,
            "data": [1] * len(skills),
        }

    # 2. Experience Timeline
    experience = extraction.get("work_experience", [])
    if experience:
        timeline = []
        for exp in experience:
            if isinstance(exp, dict):
                timeline.append({
                    "role": exp.get("job_title", "Unknown Role"),
                    "company": exp.get("company", "Unknown"),
                    "start": exp.get("start_date", ""),
                    "end": exp.get("end_date", "Present"),
                })
        charts["experience_timeline"] = {
            "type": "timeline",
            "title": "Career Timeline",
            "data": timeline,
        }

    # 3. Education overview
    education = extraction.get("educational_qualifications", [])
    if education:
        edu_data = []
        for edu in education:
            if isinstance(edu, dict):
                edu_data.append({
                    "degree": edu.get("degree", ""),
                    "field": edu.get("field_of_study", ""),
                    "institution": edu.get("institution", ""),
                    "year": edu.get("end_year", ""),
                })
        charts["education_overview"] = {
            "type": "list",
            "title": "Education",
            "data": edu_data,
        }

    return charts


def _build_research_paper_charts(extraction: Dict[str, Any]) -> Dict[str, Any]:
    """Build ECharts-ready data for research paper documents."""
    charts: Dict[str, Any] = {}

    # 1. Benchmark Results comparison (grouped bar chart)
    benchmarks = extraction.get("benchmark_results", [])
    if benchmarks:
        metrics = []
        proposed = []
        baselines = []
        for bm in benchmarks:
            if isinstance(bm, dict):
                metrics.append(bm.get("metric_name", "Unknown"))
                # Try to parse numeric values
                try:
                    proposed.append(float(bm.get("proposed_value", 0) or 0))
                except (ValueError, TypeError):
                    proposed.append(0)
                try:
                    baselines.append(float(bm.get("baseline_value", 0) or 0))
                except (ValueError, TypeError):
                    baselines.append(0)

        charts["benchmark_comparison"] = {
            "type": "grouped_bar",
            "title": "Benchmark Results: Proposed vs Baseline",
            "categories": metrics,
            "series": [
                {"name": "Proposed", "data": proposed},
                {"name": "Baseline", "data": baselines},
            ],
        }

    # 2. Key Findings word cloud (as list for now)
    findings = extraction.get("key_findings", [])
    if findings:
        charts["key_findings"] = {
            "type": "list",
            "title": "Key Findings",
            "data": findings,
        }

    # 3. Keywords
    keywords = extraction.get("keywords", [])
    if keywords:
        charts["keywords"] = {
            "type": "tags",
            "title": "Research Keywords",
            "data": keywords,
        }

    return charts


def _build_business_report_charts(extraction: Dict[str, Any]) -> Dict[str, Any]:
    """Build ECharts-ready data for business report documents."""
    charts: Dict[str, Any] = {}

    # 1. KPI Dashboard (gauge/bar)
    kpis = extraction.get("executive_kpis", [])
    if kpis:
        kpi_names = []
        kpi_values = []
        kpi_targets = []
        for kpi in kpis:
            if isinstance(kpi, dict):
                kpi_names.append(kpi.get("kpi_name", "Unknown"))
                try:
                    kpi_values.append(float(kpi.get("actual_value", 0) or 0))
                except (ValueError, TypeError):
                    kpi_values.append(0)
                try:
                    kpi_targets.append(float(kpi.get("target_or_prior_value", 0) or 0))
                except (ValueError, TypeError):
                    kpi_targets.append(0)

        charts["kpi_dashboard"] = {
            "type": "grouped_bar",
            "title": "KPI Performance: Actual vs Target",
            "categories": kpi_names,
            "series": [
                {"name": "Actual", "data": kpi_values},
                {"name": "Target/Prior", "data": kpi_targets},
            ],
        }

    # 2. Segment Breakdown (pie chart)
    segments = extraction.get("segment_breakdown", [])
    if segments:
        seg_data = []
        for seg in segments:
            if isinstance(seg, dict):
                try:
                    value = float(seg.get("share_percentage", 0) or seg.get("revenue_or_metric_value", 0) or 0)
                except (ValueError, TypeError):
                    value = 1
                seg_data.append({
                    "name": seg.get("segment_name", "Unknown"),
                    "value": value,
                })

        charts["segment_breakdown"] = {
            "type": "pie",
            "title": "Segment Breakdown",
            "data": seg_data,
        }

    # 3. Risk factors
    risks = extraction.get("risk_factors_and_anomalies", [])
    if risks:
        charts["risk_factors"] = {
            "type": "list",
            "title": "Risk Factors & Anomalies",
            "data": risks,
        }

    return charts


def build_chart_data(extraction: Dict[str, Any], document_type: str) -> Dict[str, Any]:
    """Route to the appropriate chart builder based on document type."""
    builders = {
        "resume": _build_resume_charts,
        "research_paper": _build_research_paper_charts,
        "business_analytics_report": _build_business_report_charts,
    }
    builder = builders.get(document_type, _build_resume_charts)
    return builder(extraction)


def generate_infographic_url(extraction: Dict[str, Any], document_type: str) -> Optional[str]:
    """
    Generate an AI infographic URL using Pollinations.ai.
    This is a free, keyless image generation API.
    """
    # Build a descriptive prompt from the extraction
    summary = extraction.get("summary", "")
    doc_labels = {
        "resume": "professional resume",
        "research_paper": "academic research paper",
        "business_analytics_report": "business analytics report",
    }
    doc_label = doc_labels.get(document_type, "document")

    # Build key details for the prompt
    details = []
    if document_type == "resume":
        name = extraction.get("candidate_name", "a professional")
        skills = extraction.get("skills", [])[:5]
        details.append(f"Candidate: {name}")
        if skills:
            details.append(f"Key skills: {', '.join(skills)}")
    elif document_type == "research_paper":
        title = extraction.get("paper_title", "Research Study")
        details.append(f"Paper: {title}")
    else:
        title = extraction.get("report_title", "Business Report")
        details.append(f"Report: {title}")

    detail_str = ". ".join(details)

    prompt = (
        f"Create a clean, modern, professional infographic visual summary card for a {doc_label}. "
        f"{detail_str}. "
        f"Use a sleek dark blue and teal color scheme with white text. "
        f"Include icons and data visualization elements. "
        f"Minimalist corporate design style, 16:9 aspect ratio."
    )

    encoded = urllib.parse.quote(prompt)
    url = f"{settings.POLLINATIONS_BASE_URL}/{encoded}?width=800&height=450&nologo=true"
    return url
