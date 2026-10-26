"""
Analysis route: the main pipeline endpoint.
Orchestrates extraction → LLM → validation → completeness → visuals → PostgreSQL persistence.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import crud, get_db
from app.routers.documents import get_document_data
from app.schemas.requests import AnalyzeRequest, AnalyzeResponse, VisualInsights
from app.services.completeness import compute_completeness
from app.services.llm_service import analyze_document
from app.services.visual_service import build_chart_data, generate_infographic_data

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
):
    """
    Run the full document analysis pipeline:
    1. Retrieve document text from hot cache or PostgreSQL database
    2. Call LLM with parameterized multi-domain prompt
    3. Validate extraction through polymorphic Pydantic v2 schemas
    4. Compute weighted completeness score (C_total)
    5. Generate domain-tailored visual insights and AI infographic
    6. Persist analysis results into PostgreSQL database
    """
    # 1. Retrieve document from hot cache or PostgreSQL
    doc = get_document_data(request.document_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail={
            "error_code": "DOCUMENT_NOT_FOUND",
            "message": f"Document '{request.document_id}' not found. Upload a document first or load a sample.",
            "remediation": "Use POST /api/v1/documents/upload or GET /api/v1/documents/samples/{id}/load",
        })

    document_text = doc["text"]
    text_hash = doc["content_hash"]

    # 2. LLM Analysis
    logger.info(
        f"Analyzing document '{request.document_id}' as {request.document_type} "
        f"(style={request.summary_style}, level={request.analysis_level})"
    )

    extraction = await analyze_document(
        document_text=document_text,
        text_hash=text_hash,
        document_type=request.document_type,
        summary_style=request.summary_style,
        analysis_level=request.analysis_level,
        focus_topics=request.focus_topics,
    )

    # 3. Compute Completeness Score
    completeness_score, completeness_breakdown = compute_completeness(
        extraction, request.document_type
    )

    # 4. Generate Visual Insights
    charts_data = build_chart_data(extraction, request.document_type)
    infographic_data = generate_infographic_data(extraction, request.document_type)

    summary = extraction.get("summary", "")
    uncertainty_flags = list(extraction.get("uncertainty_flags", []))

    # Auto-flag incomplete or missing dimensions detected by completeness scorer
    for dim in completeness_breakdown:
        if dim.score < 60.0:
            flag_msg = f"Missing or incomplete required data for {dim.dimension} ({dim.label})"
            if not any(dim.dimension in f.lower() for f in uncertainty_flags):
                uncertainty_flags.append(flag_msg)

    # 5. Persist Analysis Record in PostgreSQL
    try:
        crud.create_analysis(
            db=db,
            document_id=request.document_id,
            document_type=request.document_type,
            summary_style=request.summary_style,
            analysis_level=request.analysis_level,
            summary=summary,
            completeness_score=completeness_score,
            completeness_breakdown=[b.model_dump() for b in completeness_breakdown],
            extraction_payload=extraction,
            visual_insights={
                "charts_data": charts_data,
                "ai_infographic_svg": infographic_data["svg_content"],
                "generation_method": infographic_data["generation_method"],
            },
            uncertainty_flags=uncertainty_flags,
        )
    except Exception as e:
        logger.warning(f"Could not persist analysis to database: {e}")

    # 6. Build response
    return AnalyzeResponse(
        document_id=request.document_id,
        document_type=request.document_type,
        summary=summary,
        extraction=extraction,
        completeness_score=completeness_score,
        completeness_breakdown=completeness_breakdown,
        uncertainty_flags=uncertainty_flags,
        visual_insights=VisualInsights(
            charts_data=charts_data,
            ai_infographic_svg=infographic_data["svg_content"],
            generation_method=infographic_data["generation_method"],
        ),
        analysis_level=request.analysis_level,
        summary_style=request.summary_style,
    )


@router.get("/analyze/{document_id}/history")
async def get_analysis_history(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve all historical analyses for a document from PostgreSQL."""
    try:
        records = crud.list_analyses_for_document(db=db, document_id=document_id)
        return [r.to_dict() for r in records]
    except Exception as e:
        logger.error(f"Error fetching analysis history: {e}")
        return []
