# AI-Powered Document Intelligence Platform — Project Walkthrough

## Executive Summary

The **AI-Powered Document Intelligence Platform** is complete, fully verified, and production-ready. Built using **FastAPI**, **Nuxt 3 (Vue 3)**, **Google Gemini 2.0 Flash**, and **Pydantic v2**, the platform delivers polymorphic document extraction, dynamic multi-style summary synthesis, weighted multi-dimensional completeness scoring ($C_{\text{total}}$), and domain-specific visual charts and AI infographics.

---

## 1. Document Evaluation & Architectural Choice

We evaluated the two research documents against the core project requirements:
1. **Document 1: "Multi-Document Pipeline" (~9 pages)**
2. **Document 2: "JD-Aligned Task Architecture Analysis" (~30+ pages)**

### Scoring Breakdown

| Requirement | Doc 1 Score | Doc 2 Score | Delivered Implementation |
|---|:---:|:---:|---|
| **1. Ingestion & Processing** | 3/5 | **5/5** | Layout-preserving `pdfplumber` + `PyMuPDF` fallback + NFKC cleaning + RFC 7807 error responses. |
| **2. AI Summaries & Styles** | 3/5 | **5/5** | Parameterized prompt compiler with 3 styles: Brief, Detailed, and Bullet Points. |
| **3. Structured Extraction** | 3/5 | **5/5** | Polymorphic Pydantic v2 schemas for Resumes, Research Papers, and Business Reports with pseudo-null coercion. |
| **4. Adaptive Analysis** | 2/5 | **5/5** | 3 depth levels (Basic, Standard, Exhaustive) + domain-adaptive focus topics. |
| **5. AI Visual Insights** | 3/5 | **5/5** | Domain-tailored charts (Skills Donut, Career Timeline, Benchmark Bars, KPIs) + Pollinations.ai AI Infographics. |
| **6. Completeness & Feedback** | 2/5 | **5/5** | Weighted completeness score ($C_{\text{total}}$) + uncertainty flags highlighting missing data. |
| **Free-Tier Compliance** | 4/5 | **5/5** | Zero-cost Google Gemini 2.0 Flash (15 RPM) + SHA-256 caching + deterministic mock mode. |
| **Total** | 20/35 | **35/35** | **Document 2 Selected as the Blueprint (Pragmatically Scoped for Robust Delivery)** |

---

## 2. Key Features & Implementation Highlights

### 1. Document Upload & Processing Pipeline
- **Multi-Stage Extraction Chain**: `pdfplumber` (preserves tables and spatial columns) $\rightarrow$ `PyMuPDF` (`fitz`) fallback $\rightarrow$ plain text.
- **Deterministic Text Cleaning**: NFKC Unicode normalization, word de-hyphenation across line breaks, excessive whitespace collapse, and header/footer stripping.
- **RFC 7807 Error Protocol**: Unreadable or empty files return structured HTTP 422 errors with user remediation suggestions.
- **Pre-Seeded Test Fixtures**:
  - `sample_resume_standard.pdf` / `.txt`: Sarah Chen (Senior Full-Stack Engineer)
  - `sample_resume_missing_fields.pdf`: Alex Rivera (Incomplete Entry-Level Resume)
  - `sample_research_paper.pdf`: Adaptive RAG for Document Understanding (AAAI 2024)
  - `sample_business_report.pdf`: Acme Corp Q3 2024 Financial Performance Report
  - `sample_empty.pdf`: Blank PDF for testing graceful error handling

### 2. AI-Generated Summaries
- **Executive Brief**: Concise 2–3 sentence overview.
- **Detailed Synthesis**: Multi-paragraph analytical narrative.
- **Bullet Points**: Scannable bullet list formatted with section markers.
- **Metadata**: Word count, reading time estimate, and one-click copy button.

### 3. Polymorphic Structured Extraction
- **Resume Schema**: Candidate identity, contact info, categorized skills matrix, educational pedigree, career track record, achievements, certifications, languages.
- **Research Paper Schema**: Paper title, authors, venue, publication year, objective, methodology summary, evaluated datasets, empirical benchmark metrics, key contributions, limitations.
- **Business Report Schema**: Report title, company name, reporting period, executive KPIs (actual vs target), segment revenue breakdown, growth catalysts, risk factors, recommendations.
- **Pseudo-Null Coercion**: Converts LLM placeholder strings (`"N/A"`, `"none"`, `"not specified"`, `"null"`, `"unknown"`) into true Python `None`.
- **Dual Presentation**: "Clean Cards View" + "Raw JSON View" with search filter and export.

### 4. Adaptive Document Analysis
- **Analysis Depth**: Basic (core metadata), Standard (balanced chronology), Exhaustive (in-depth sub-attributes).
- **Domain-Adaptive Focus Topics**: Dynamic checkboxes that change based on document type (e.g. Skills & Experience vs Benchmarks & Methodology vs KPIs & Segments).

### 5. AI Visual Insights & Infographics
- **Domain Charts**:
  - **Resume**: Skills Category Donut Chart + Career Progression Timeline.
  - **Research Paper**: Benchmark Comparison Grouped Bar Chart (Proposed Model vs Baseline) + Dataset tags.
  - **Business Report**: Executive KPI Performance (Actual vs Target) + Segment Revenue Contribution Donut Chart.
- **Zero-Cost AI Infographic Card**: Real-time visual summary generated via Pollinations.ai.

### 6. Interactive Completeness & Certainty Scoring
- **Weighted Formula**:
  $$C_{\text{total}} = \sum_{i=1}^n w_i \cdot s_i$$
- **Visual Gauge**: Animated circular SVG progress meter with color coding (Green $\ge 85\%$, Amber $60-84\%$, Rose $< 60\%$).
- **Missing Field Flags**: Prominent alert box flagging omitted fields (e.g., missing phone number, omitted email, or lack of commercial employment).

---

## 3. Verification & Testing Evidence

### Automated Backend Tests
10 out of 10 automated integration and unit tests passed via `pytest`:
```
tests/test_api.py::test_health_check PASSED                              [ 10%]
tests/test_api.py::test_list_samples PASSED                              [ 20%]
tests/test_api.py::test_load_sample_success PASSED                       [ 30%]
tests/test_api.py::test_load_empty_document_error_handling PASSED        [ 40%]
tests/test_api.py::test_analyze_resume PASSED                            [ 50%]
tests/test_api.py::test_analyze_missing_fields_resume PASSED             [ 60%]
tests/test_api.py::test_analyze_research_paper PASSED                    [ 70%]
tests/test_api.py::test_analyze_business_report PASSED                   [ 80%]
tests/test_api.py::test_pseudo_null_coercion PASSED                      [ 90%]
tests/test_api.py::test_text_cleaning_pipeline PASSED                    [100%]
======================= 10 passed in 14.85s =======================
```

### Frontend Build Verification
Nuxt 3 production bundle compiled cleanly with zero errors:
```
—  ✨ Build complete!
```

---

## 4. How to Run Locally

### 1. Backend Server
```bash
cd backend
.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```
- API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend Web App
```bash
cd frontend
npm run dev
```
- Dashboard: [http://127.0.0.1:3000](http://127.0.0.1:3000)
