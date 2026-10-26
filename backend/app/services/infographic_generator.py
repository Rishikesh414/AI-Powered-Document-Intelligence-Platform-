"""
Dynamic SVG Infographic Generator.
Replaces the broken Pollinations.ai dependency with a zero-dependency,
server-side SVG generator that creates beautiful, data-driven infographics
from document extraction data.

Supports: Resume, Research Paper, Business Analytics Report
"""

from __future__ import annotations

import html
import math
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Color Palettes per document type
# ---------------------------------------------------------------------------

PALETTES = {
    "resume": {
        "bg_gradient_start": "#0F172A",
        "bg_gradient_end": "#1E293B",
        "accent": "#06B6D4",
        "accent_light": "#22D3EE",
        "secondary": "#8B5CF6",
        "text_primary": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "card_bg": "rgba(30, 41, 59, 0.8)",
        "badge_bg": "rgba(6, 182, 212, 0.15)",
        "badge_border": "rgba(6, 182, 212, 0.4)",
        "divider": "rgba(148, 163, 184, 0.2)",
        "bar_colors": ["#06B6D4", "#8B5CF6", "#F472B6", "#34D399", "#FBBF24", "#FB923C"],
    },
    "research_paper": {
        "bg_gradient_start": "#0C0A1A",
        "bg_gradient_end": "#1A1433",
        "accent": "#A78BFA",
        "accent_light": "#C4B5FD",
        "secondary": "#F472B6",
        "text_primary": "#F1F5F9",
        "text_secondary": "#A1A1AA",
        "card_bg": "rgba(26, 20, 51, 0.8)",
        "badge_bg": "rgba(167, 139, 250, 0.15)",
        "badge_border": "rgba(167, 139, 250, 0.4)",
        "divider": "rgba(161, 161, 170, 0.2)",
        "bar_colors": ["#A78BFA", "#F472B6", "#34D399", "#FBBF24", "#06B6D4", "#FB923C"],
    },
    "business_analytics_report": {
        "bg_gradient_start": "#0A1628",
        "bg_gradient_end": "#132240",
        "accent": "#3B82F6",
        "accent_light": "#60A5FA",
        "secondary": "#10B981",
        "text_primary": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "card_bg": "rgba(19, 34, 64, 0.8)",
        "badge_bg": "rgba(59, 130, 246, 0.15)",
        "badge_border": "rgba(59, 130, 246, 0.4)",
        "divider": "rgba(148, 163, 184, 0.2)",
        "bar_colors": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"],
    },
}


def _esc(text: str) -> str:
    """Escape text for safe SVG embedding."""
    return html.escape(str(text), quote=True)


def _truncate(text: str, max_len: int = 40) -> str:
    """Truncate long text with ellipsis."""
    if len(text) > max_len:
        return text[:max_len - 1] + "…"
    return text


# ---------------------------------------------------------------------------
# Common SVG fragments
# ---------------------------------------------------------------------------

def _svg_header(width: int, height: int, palette: dict) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{palette['bg_gradient_start']}" />
      <stop offset="100%" style="stop-color:{palette['bg_gradient_end']}" />
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{palette['accent']}" />
      <stop offset="100%" style="stop-color:{palette['accent_light']}" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="rgba(0,0,0,0.3)" />
    </filter>
    <clipPath id="rounded">
      <rect x="0" y="0" width="{width}" height="{height}" rx="16" ry="16" />
    </clipPath>
  </defs>
  <g clip-path="url(#rounded)">
  <rect width="{width}" height="{height}" fill="url(#bgGrad)" rx="16" ry="16"/>
  <!-- Decorative circles -->
  <circle cx="{width - 60}" cy="60" r="120" fill="{palette['accent']}" opacity="0.04" />
  <circle cx="80" cy="{height - 40}" r="80" fill="{palette['secondary']}" opacity="0.05" />
'''


def _svg_footer() -> str:
    return "  </g>\n</svg>"


def _badge(x: int, y: int, text: str, palette: dict, idx: int = 0) -> str:
    """Render a small rounded badge."""
    t = _esc(_truncate(text, 18))
    # Estimate width based on character count
    w = max(len(t) * 7 + 16, 50)
    color = palette["bar_colors"][idx % len(palette["bar_colors"])]
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" '
        f'fill="{color}" opacity="0.15" stroke="{color}" stroke-width="0.5" />'
        f'<text x="{x + w // 2}" y="{y + 15}" font-family="Inter, system-ui, sans-serif" '
        f'font-size="10" fill="{color}" text-anchor="middle" font-weight="500">{t}</text>'
    )


def _section_title(x: int, y: int, icon: str, title: str, palette: dict) -> str:
    """Render a section title with icon."""
    return (
        f'<text x="{x}" y="{y}" font-family="Inter, system-ui, sans-serif" '
        f'font-size="11" fill="{palette["accent"]}" font-weight="600" '
        f'text-transform="uppercase" letter-spacing="1.5">'
        f'{icon}  {_esc(title)}</text>'
    )


def _horizontal_bar(x: int, y: int, width: int, value: float, max_val: float,
                     label: str, palette: dict, idx: int = 0) -> str:
    """Render a horizontal bar with label."""
    bar_width = int((value / max_val) * width) if max_val > 0 else 0
    bar_width = max(bar_width, 4)
    color = palette["bar_colors"][idx % len(palette["bar_colors"])]
    return (
        f'<text x="{x}" y="{y - 4}" font-family="Inter, system-ui, sans-serif" '
        f'font-size="10" fill="{palette["text_secondary"]}">{_esc(_truncate(label, 22))}</text>'
        f'<rect x="{x}" y="{y}" width="{width}" height="8" rx="4" '
        f'fill="{palette["divider"]}" />'
        f'<rect x="{x}" y="{y}" width="{bar_width}" height="8" rx="4" '
        f'fill="{color}" />'
        f'<text x="{x + width + 8}" y="{y + 8}" font-family="Inter, system-ui, sans-serif" '
        f'font-size="9" fill="{palette["text_secondary"]}">{value:.0f}</text>'
    )


def _donut_segment(cx: int, cy: int, r: int, start_pct: float, end_pct: float,
                   color: str, stroke_width: int = 12) -> str:
    """Render a donut segment arc."""
    circumference = 2 * math.pi * r
    start_offset = circumference * (1 - start_pct)
    dash_len = circumference * (end_pct - start_pct)
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
        f'stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-dasharray="{dash_len:.1f} {circumference - dash_len:.1f}" '
        f'stroke-dashoffset="{start_offset:.1f}" '
        f'transform="rotate(-90 {cx} {cy})" />'
    )


# ---------------------------------------------------------------------------
# Document-type specific generators
# ---------------------------------------------------------------------------

def _generate_resume_svg(extraction: Dict[str, Any]) -> str:
    """Generate SVG infographic for resume documents."""
    palette = PALETTES["resume"]
    W, H = 800, 450
    parts: List[str] = [_svg_header(W, H, palette)]

    name = extraction.get("candidate_name", "Professional Profile")
    email = extraction.get("email", "")
    phone = extraction.get("phone", "")
    summary = extraction.get("summary", "")

    # --- Header strip ---
    parts.append(
        f'<rect x="0" y="0" width="{W}" height="70" fill="{palette["accent"]}" opacity="0.08" />'
        f'<line x1="0" y1="70" x2="{W}" y2="70" stroke="{palette["divider"]}" stroke-width="1" />'
    )
    # Name
    parts.append(
        f'<text x="32" y="35" font-family="Inter, system-ui, sans-serif" font-size="22" '
        f'font-weight="700" fill="{palette["text_primary"]}">{_esc(_truncate(name, 35))}</text>'
    )
    # Contact info
    contact_parts = []
    if email:
        contact_parts.append(_esc(_truncate(email, 30)))
    if phone:
        contact_parts.append(_esc(phone))
    if contact_parts:
        parts.append(
            f'<text x="32" y="55" font-family="Inter, system-ui, sans-serif" font-size="10" '
            f'fill="{palette["text_secondary"]}">{" · ".join(contact_parts)}</text>'
        )

    # Type badge
    parts.append(
        f'<rect x="{W - 140}" y="22" width="110" height="26" rx="13" '
        f'fill="{palette["accent"]}" opacity="0.15" stroke="{palette["accent"]}" stroke-width="0.5" />'
        f'<text x="{W - 85}" y="39" font-family="Inter, system-ui, sans-serif" font-size="10" '
        f'fill="{palette["accent"]}" text-anchor="middle" font-weight="600">📄 RESUME</text>'
    )

    # --- Left column: Skills ---
    col_x = 32
    y = 95
    skills = extraction.get("skills", [])[:8]
    categorized = extraction.get("categorized_skills", [])

    parts.append(_section_title(col_x, y, "◆", "SKILLS", palette))
    y += 20

    if categorized:
        # Show categorized skills as bars
        max_count = max((len(c.get("skills", [])) for c in categorized if isinstance(c, dict)), default=1)
        for i, cat in enumerate(categorized[:5]):
            if isinstance(cat, dict):
                cat_name = cat.get("category", "Other")
                cat_skills = cat.get("skills", [])
                parts.append(_horizontal_bar(col_x, y, 200, len(cat_skills), max_count, cat_name, palette, i))
                y += 28
    elif skills:
        # Show skills as badges
        bx = col_x
        for i, skill in enumerate(skills):
            t = _truncate(str(skill), 18)
            w = max(len(t) * 7 + 16, 50)
            if bx + w > 280:
                bx = col_x
                y += 28
            parts.append(_badge(bx, y, str(skill), palette, i))
            bx += w + 6
        y += 32

    # --- Left column: Experience ---
    y += 10
    experience = extraction.get("work_experience", [])[:3]
    if experience:
        parts.append(_section_title(col_x, y, "◆", "EXPERIENCE", palette))
        y += 18
        for exp in experience:
            if isinstance(exp, dict):
                role = _esc(_truncate(exp.get("job_title", ""), 28))
                company = _esc(_truncate(exp.get("company", ""), 22))
                period = f'{exp.get("start_date", "")} — {exp.get("end_date", "Present")}'
                parts.append(
                    f'<text x="{col_x}" y="{y}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="11" fill="{palette["text_primary"]}" font-weight="600">{role}</text>'
                    f'<text x="{col_x}" y="{y + 14}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="9" fill="{palette["text_secondary"]}">{company} · {_esc(period)}</text>'
                )
                y += 36

    # --- Right column: Education + Summary ---
    rx = 420
    ry = 95
    education = extraction.get("educational_qualifications", [])[:3]
    if education:
        parts.append(_section_title(rx, ry, "◆", "EDUCATION", palette))
        ry += 18
        for edu in education:
            if isinstance(edu, dict):
                degree = _esc(_truncate(edu.get("degree", ""), 30))
                institution = _esc(_truncate(edu.get("institution", ""), 28))
                parts.append(
                    f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="11" fill="{palette["text_primary"]}" font-weight="600">{degree}</text>'
                    f'<text x="{rx}" y="{ry + 14}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="9" fill="{palette["text_secondary"]}">{institution}</text>'
                )
                ry += 36

    # Summary snippet
    if summary:
        ry += 10
        parts.append(_section_title(rx, ry, "◆", "PROFILE SUMMARY", palette))
        ry += 16
        # Wrap summary text
        words = summary.split()
        line = ""
        line_count = 0
        for word in words:
            test = line + " " + word if line else word
            if len(test) > 45:
                parts.append(
                    f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}</text>'
                )
                ry += 14
                line = word
                line_count += 1
                if line_count >= 6:
                    parts.append(
                        f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                        f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}…</text>'
                    )
                    break
            else:
                line = test
        else:
            if line and line_count < 6:
                parts.append(
                    f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}</text>'
                )

    # --- Footer strip ---
    parts.append(
        f'<rect x="0" y="{H - 32}" width="{W}" height="32" fill="{palette["accent"]}" opacity="0.05" />'
        f'<text x="{W // 2}" y="{H - 12}" font-family="Inter, system-ui, sans-serif" font-size="9" '
        f'fill="{palette["text_secondary"]}" text-anchor="middle" opacity="0.6">'
        f'Generated by DocuIntel AI · Document Intelligence Platform</text>'
    )

    parts.append(_svg_footer())
    return "\n".join(parts)


def _generate_research_paper_svg(extraction: Dict[str, Any]) -> str:
    """Generate SVG infographic for research paper documents."""
    palette = PALETTES["research_paper"]
    W, H = 800, 450
    parts: List[str] = [_svg_header(W, H, palette)]

    title = extraction.get("paper_title", "Research Paper")
    authors = extraction.get("authors", [])
    summary = extraction.get("summary", "")

    # --- Header ---
    parts.append(
        f'<rect x="0" y="0" width="{W}" height="80" fill="{palette["accent"]}" opacity="0.06" />'
        f'<line x1="0" y1="80" x2="{W}" y2="80" stroke="{palette["divider"]}" stroke-width="1" />'
    )
    parts.append(
        f'<text x="32" y="32" font-family="Inter, system-ui, sans-serif" font-size="20" '
        f'font-weight="700" fill="{palette["text_primary"]}">{_esc(_truncate(title, 55))}</text>'
    )

    # Authors
    if authors:
        author_str = ", ".join(str(a) for a in authors[:4])
        if len(authors) > 4:
            author_str += f" +{len(authors) - 4} more"
        parts.append(
            f'<text x="32" y="52" font-family="Inter, system-ui, sans-serif" font-size="10" '
            f'fill="{palette["text_secondary"]}">{_esc(_truncate(author_str, 70))}</text>'
        )

    # Type badge
    parts.append(
        f'<rect x="{W - 170}" y="18" width="140" height="26" rx="13" '
        f'fill="{palette["accent"]}" opacity="0.15" stroke="{palette["accent"]}" stroke-width="0.5" />'
        f'<text x="{W - 100}" y="35" font-family="Inter, system-ui, sans-serif" font-size="10" '
        f'fill="{palette["accent"]}" text-anchor="middle" font-weight="600">📑 RESEARCH PAPER</text>'
    )

    # Publication info
    venue = extraction.get("publication_venue", "")
    year = extraction.get("publication_year", "")
    if venue or year:
        info_str = f"{venue} · {year}" if venue and year else (venue or year)
        parts.append(
            f'<text x="32" y="68" font-family="Inter, system-ui, sans-serif" font-size="9" '
            f'fill="{palette["accent"]}" opacity="0.8">{_esc(_truncate(str(info_str), 60))}</text>'
        )

    # --- Left column: Benchmark Results ---
    y = 105
    benchmarks = extraction.get("benchmark_results", [])[:5]
    if benchmarks:
        parts.append(_section_title(32, y, "◆", "BENCHMARK RESULTS", palette))
        y += 20
        numeric_benchmarks = []
        for bm in benchmarks:
            if isinstance(bm, dict):
                try:
                    val = float(bm.get("proposed_value", 0) or 0)
                    numeric_benchmarks.append((bm.get("metric_name", "Metric"), val))
                except (ValueError, TypeError):
                    pass
        if numeric_benchmarks:
            max_val = max(v for _, v in numeric_benchmarks) or 1
            for i, (label, val) in enumerate(numeric_benchmarks):
                parts.append(_horizontal_bar(32, y, 280, val, max_val, label, palette, i))
                y += 28

    # --- Left column: Key Findings ---
    findings = extraction.get("key_findings", [])[:4]
    if findings:
        y += 10
        parts.append(_section_title(32, y, "◆", "KEY FINDINGS", palette))
        y += 16
        for i, finding in enumerate(findings):
            parts.append(
                f'<circle cx="40" cy="{y - 3}" r="3" fill="{palette["bar_colors"][i % len(palette["bar_colors"])]}" />'
                f'<text x="50" y="{y}" font-family="Inter, system-ui, sans-serif" font-size="10" '
                f'fill="{palette["text_secondary"]}">{_esc(_truncate(str(finding), 42))}</text>'
            )
            y += 18

    # --- Right column: Keywords + Abstract ---
    rx = 420
    ry = 105
    keywords = extraction.get("keywords", [])[:10]
    if keywords:
        parts.append(_section_title(rx, ry, "◆", "KEYWORDS", palette))
        ry += 20
        bx = rx
        for i, kw in enumerate(keywords):
            t = _truncate(str(kw), 16)
            w = max(len(t) * 7 + 16, 50)
            if bx + w > W - 30:
                bx = rx
                ry += 26
            parts.append(_badge(bx, ry, str(kw), palette, i))
            bx += w + 6
        ry += 34

    # Abstract / Summary
    if summary:
        ry += 5
        parts.append(_section_title(rx, ry, "◆", "ABSTRACT", palette))
        ry += 16
        words = summary.split()
        line = ""
        line_count = 0
        for word in words:
            test = line + " " + word if line else word
            if len(test) > 45:
                parts.append(
                    f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}</text>'
                )
                ry += 14
                line = word
                line_count += 1
                if line_count >= 8:
                    parts.append(
                        f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                        f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}…</text>'
                    )
                    break
            else:
                line = test
        else:
            if line and line_count < 8:
                parts.append(
                    f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}</text>'
                )

    # Footer
    parts.append(
        f'<rect x="0" y="{H - 32}" width="{W}" height="32" fill="{palette["accent"]}" opacity="0.05" />'
        f'<text x="{W // 2}" y="{H - 12}" font-family="Inter, system-ui, sans-serif" font-size="9" '
        f'fill="{palette["text_secondary"]}" text-anchor="middle" opacity="0.6">'
        f'Generated by DocuIntel AI · Document Intelligence Platform</text>'
    )

    parts.append(_svg_footer())
    return "\n".join(parts)


def _generate_business_report_svg(extraction: Dict[str, Any]) -> str:
    """Generate SVG infographic for business analytics reports."""
    palette = PALETTES["business_analytics_report"]
    W, H = 800, 450
    parts: List[str] = [_svg_header(W, H, palette)]

    title = extraction.get("report_title", "Business Analytics Report")
    company = extraction.get("company_name", "")
    period = extraction.get("reporting_period", "")
    summary = extraction.get("summary", "")

    # --- Header ---
    parts.append(
        f'<rect x="0" y="0" width="{W}" height="75" fill="{palette["accent"]}" opacity="0.06" />'
        f'<line x1="0" y1="75" x2="{W}" y2="75" stroke="{palette["divider"]}" stroke-width="1" />'
    )
    parts.append(
        f'<text x="32" y="33" font-family="Inter, system-ui, sans-serif" font-size="20" '
        f'font-weight="700" fill="{palette["text_primary"]}">{_esc(_truncate(str(title), 50))}</text>'
    )
    sub_parts = []
    if company:
        sub_parts.append(_esc(_truncate(str(company), 25)))
    if period:
        sub_parts.append(_esc(_truncate(str(period), 25)))
    if sub_parts:
        parts.append(
            f'<text x="32" y="52" font-family="Inter, system-ui, sans-serif" font-size="10" '
            f'fill="{palette["text_secondary"]}">{" · ".join(sub_parts)}</text>'
        )

    # Type badge
    parts.append(
        f'<rect x="{W - 180}" y="18" width="150" height="26" rx="13" '
        f'fill="{palette["accent"]}" opacity="0.15" stroke="{palette["accent"]}" stroke-width="0.5" />'
        f'<text x="{W - 105}" y="35" font-family="Inter, system-ui, sans-serif" font-size="10" '
        f'fill="{palette["accent"]}" text-anchor="middle" font-weight="600">📊 BUSINESS REPORT</text>'
    )

    # --- Left column: KPIs ---
    y = 100
    kpis = extraction.get("executive_kpis", [])[:5]
    if kpis:
        parts.append(_section_title(32, y, "◆", "KEY PERFORMANCE INDICATORS", palette))
        y += 20
        for i, kpi in enumerate(kpis):
            if isinstance(kpi, dict):
                kpi_name = _esc(_truncate(kpi.get("kpi_name", "Metric"), 22))
                try:
                    actual = float(kpi.get("actual_value", 0) or 0)
                except (ValueError, TypeError):
                    actual = 0
                try:
                    target = float(kpi.get("target_or_prior_value", 0) or 0)
                except (ValueError, TypeError):
                    target = 0

                color = palette["bar_colors"][i % len(palette["bar_colors"])]
                pct = (actual / target * 100) if target > 0 else 0
                pct_display = min(pct, 100)

                # KPI card
                parts.append(
                    f'<text x="32" y="{y}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="10" fill="{palette["text_secondary"]}">{kpi_name}</text>'
                    f'<rect x="32" y="{y + 4}" width="200" height="6" rx="3" '
                    f'fill="{palette["divider"]}" />'
                    f'<rect x="32" y="{y + 4}" width="{int(pct_display * 2)}" height="6" rx="3" '
                    f'fill="{color}" />'
                    f'<text x="240" y="{y + 10}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="9" fill="{color}" font-weight="600">{pct:.0f}%</text>'
                )
                y += 26

    # --- Left column: Segments (donut chart) ---
    segments = extraction.get("segment_breakdown", [])[:6]
    if segments:
        y += 15
        parts.append(_section_title(32, y, "◆", "SEGMENT BREAKDOWN", palette))
        y += 10
        cx, cy = 110, y + 60
        r = 40
        total = 0
        seg_data = []
        for seg in segments:
            if isinstance(seg, dict):
                try:
                    val = float(seg.get("share_percentage", 0) or seg.get("revenue_or_metric_value", 0) or 1)
                except (ValueError, TypeError):
                    val = 1
                seg_data.append((seg.get("segment_name", "Other"), val))
                total += val

        if total > 0:
            start = 0
            for i, (name, val) in enumerate(seg_data):
                pct = val / total
                color = palette["bar_colors"][i % len(palette["bar_colors"])]
                parts.append(_donut_segment(cx, cy, r, start, start + pct, color, 14))
                start += pct

            # Center text
            parts.append(
                f'<text x="{cx}" y="{cy + 4}" font-family="Inter, system-ui, sans-serif" '
                f'font-size="10" fill="{palette["text_primary"]}" text-anchor="middle" '
                f'font-weight="600">{len(seg_data)}</text>'
                f'<text x="{cx}" y="{cy + 16}" font-family="Inter, system-ui, sans-serif" '
                f'font-size="8" fill="{palette["text_secondary"]}" text-anchor="middle">Segments</text>'
            )

            # Legend
            lx = 170
            ly = y + 30
            for i, (name, val) in enumerate(seg_data):
                color = palette["bar_colors"][i % len(palette["bar_colors"])]
                parts.append(
                    f'<rect x="{lx}" y="{ly}" width="8" height="8" rx="2" fill="{color}" />'
                    f'<text x="{lx + 14}" y="{ly + 8}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="9" fill="{palette["text_secondary"]}">'
                    f'{_esc(_truncate(str(name), 18))} ({val:.0f}%)</text>'
                )
                ly += 16

    # --- Right column: Risks + Summary ---
    rx = 420
    ry = 100
    risks = extraction.get("risk_factors_and_anomalies", [])[:4]
    if risks:
        parts.append(_section_title(rx, ry, "◆", "RISK FACTORS", palette))
        ry += 16
        for i, risk in enumerate(risks):
            parts.append(
                f'<text x="{rx + 14}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                f'font-size="10" fill="{palette["text_secondary"]}">⚠ {_esc(_truncate(str(risk), 40))}</text>'
            )
            ry += 18

    # Summary
    if summary:
        ry += 15
        parts.append(_section_title(rx, ry, "◆", "EXECUTIVE SUMMARY", palette))
        ry += 16
        words = summary.split()
        line = ""
        line_count = 0
        for word in words:
            test = line + " " + word if line else word
            if len(test) > 45:
                parts.append(
                    f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}</text>'
                )
                ry += 14
                line = word
                line_count += 1
                if line_count >= 7:
                    parts.append(
                        f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                        f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}…</text>'
                    )
                    break
            else:
                line = test
        else:
            if line and line_count < 7:
                parts.append(
                    f'<text x="{rx}" y="{ry}" font-family="Inter, system-ui, sans-serif" '
                    f'font-size="10" fill="{palette["text_secondary"]}">{_esc(line)}</text>'
                )

    # Footer
    parts.append(
        f'<rect x="0" y="{H - 32}" width="{W}" height="32" fill="{palette["accent"]}" opacity="0.05" />'
        f'<text x="{W // 2}" y="{H - 12}" font-family="Inter, system-ui, sans-serif" font-size="9" '
        f'fill="{palette["text_secondary"]}" text-anchor="middle" opacity="0.6">'
        f'Generated by DocuIntel AI · Document Intelligence Platform</text>'
    )

    parts.append(_svg_footer())
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_infographic_svg(extraction: Dict[str, Any], document_type: str) -> str:
    """
    Generate a dynamic SVG infographic from document extraction data.

    Returns the raw SVG string. This replaces the broken Pollinations.ai
    dependency with a zero-external-dependency, server-side solution.
    """
    generators = {
        "resume": _generate_resume_svg,
        "research_paper": _generate_research_paper_svg,
        "business_analytics_report": _generate_business_report_svg,
    }
    generator = generators.get(document_type, _generate_resume_svg)
    return generator(extraction)
