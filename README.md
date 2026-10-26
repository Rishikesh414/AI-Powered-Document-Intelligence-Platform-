# DocuIntel AI — AI-Powered Document Intelligence Platform

> **An interactive, polymorphic AI document intelligence platform built with FastAPI, Nuxt 3 (Vue 3), Google Gemini 2.5 Flash, PostgreSQL (with SQLite backup), and Pydantic v2.**  
> Automatically ingests unstructured documents (PDF, TXT, DOCX), extracts typed polymorphic entities, generates multi-style summaries, computes weighted multi-dimensional completeness scores ($C_{\text{total}}$), and renders domain-specific SVG charts and AI infographics.


### **AI-Powered Document Intelligence Platform**
*Full-Stack & Applied AI Engineer | FastAPI, Nuxt 3, Google Gemini 2.5 Flash, PostgreSQL, Pydantic v2*

- **Polymorphic Extraction Pipeline**: Architected an end-to-end document intelligence platform that ingests complex PDFs, TXT, and DOCX files, executing multi-stage layout extraction (`pdfplumber` $\rightarrow$ `PyMuPDF` fallback) and enforcing polymorphic domain schemas (Resumes, Academic Papers, Financial Reports).
- **Gemini 2.5 Flash Integration**: Integrated Google Gemini 2.5 Flash with structured JSON output enforcement, SHA-256 caching, and parameterized prompt synthesis across 3 depth levels (Basic, Standard, Exhaustive) and 3 summary styles.
- **Weighted Completeness Engine**: Formulated a multi-attribute completeness metric ($C_{\text{total}} = \sum w_i \cdot s_i$) with automated pseudo-null coercion (`"N/A"` $\rightarrow$ `None`) to detect missing fields and measure extraction integrity.
- **Two-Tier Resilient Persistence**: Implemented a self-healing database tier using Cloud PostgreSQL (Neon) as primary with zero-downtime automated failover to local SQLite (`docuintel.db`), ensuring 100% platform availability.
- **Dynamic Visuals & SVG Synthesis**: Developed a zero-cost server-side SVG infographic and chart engine generating domain-specific interactive visual summaries (career progression timelines, skill donuts, financial KPIs) with SVG export capabilities.
- **Automated Verification**: Built a comprehensive 12-test integration suite covering RFC 7807 error contracts, failover triggers, and live multi-domain analysis.

---

## 🏛️ System Architecture

The DocuIntel AI platform follows a decoupled, resilient 5-tier architecture:

```mermaid
flowchart TD
    subgraph ClientLayer ["1. PRESENTATION LAYER (Nuxt 3 / Vue 3 + TypeScript)"]
        Uploader["Document Uploader\n(Drag & Drop, 10MB Preflight, 6 Sample Fixtures)"]
        Controls["Adaptive Controls\n(Domain | Summary Style | Depth | Focus Topics)"]
        ResultsView["Results Dashboard\n(Completeness Gauge, Cards, JSON, Visuals)"]
        StatusPill["Live Health & Model Pill\n(Gemini 2.5 / Mock Mode Indicator)"]
    end

    subgraph GatewayLayer ["2. API & INGESTION GATEWAY (FastAPI / Uvicorn)"]
        CORS["CORS & Request Preflight"]
        RouterDoc["/api/v1/documents\n(Upload, Store, List Fixtures)"]
        RouterAnalyze["/api/v1/analyze\n(Extraction, Scoring, Visuals)"]
        RouterHealth["/api/v1/health\n(DB & LLM Readiness Probe)"]
        FileStorage["Local File Store\n(backend/uploads/)"]
    end

    subgraph IngestionPipeline ["3. INGESTION & TEXT NORMALIZATION"]
        Extractor["Multi-Stage Extractor\n(pdfplumber -> PyMuPDF fallback -> Plaintext)"]
        Cleaner["Text Cleaner\n(NFKC Normalize, De-hyphenate, Header/Footer Strip)"]
    end

    subgraph IntelligenceLayer ["4. REASONING & EXTRACTION ENGINE"]
        PromptCompiler["Parameterized Prompt Compiler\n(Domain Rules, Focus Topics, Token Guard)"]
        GeminiLLM["Google Gemini 2.5 Flash\n(Structured JSON Response, 15 RPM Free Tier)"]
        Cache["SHA-256 Deterministic Cache\n(Instant Zero-Cost Hits)"]
        MockLLM["Deterministic Mock Mode\n(High-Fidelity Offline Engine)"]
        PydanticEngine["Pydantic v2 Polymorphic Models\n(Resume | Research | Business + Null Coercion)"]
        CompletenessEngine["Completeness Engine\n(Domain-Weighted C_total Score & Flags)"]
        SVGVisualEngine["Server-Side SVG & Visual Engine\n(Domain Charts + Infographic Card)"]
    end

    subgraph StorageLayer ["5. PERSISTENCE & STORAGE TIER (Two-Tier Failover)"]
        DBManager["Database Connection Manager\n(Health Probe & Auto-Failover)"]
        PrimaryPG[("Primary: Neon Cloud PostgreSQL\n(documents, analyses tables)")]
        FallbackSQLite[("Fallback: Local SQLite Backup\n(docuintel.db local file)")]
    end

    %% Flow connections
    Uploader --> RouterDoc
    Controls --> RouterAnalyze
    RouterDoc --> FileStorage
    RouterDoc --> Extractor
    Extractor --> Cleaner
    Cleaner --> PromptCompiler
    RouterAnalyze --> PromptCompiler
    PromptCompiler --> Cache
    Cache -- Miss --> GeminiLLM
    GeminiLLM -- Fallback / Offline --> MockLLM
    GeminiLLM --> PydanticEngine
    MockLLM --> PydanticEngine
    PydanticEngine --> CompletenessEngine
    PydanticEngine --> SVGVisualEngine
    CompletenessEngine --> RouterAnalyze
    SVGVisualEngine --> RouterAnalyze
    RouterAnalyze --> DBManager
    RouterDoc --> DBManager
    DBManager --> PrimaryPG
    PrimaryPG -. Failover .-> FallbackSQLite
    RouterAnalyze --> ResultsView
    RouterHealth --> StatusPill
```

---

## 🔄 User Flow Diagram

The diagram below reflects the exact interactive application workflow:

```mermaid
flowchart TD
    Start([Start]) --> Visit["Visit Document Analysis Platform"]
    Visit --> UploadScreen["Upload Document Screen"]
    
    UploadScreen --> ChooseMethod{"Choose Input Method"}
    ChooseMethod -->|"Upload File"| DragSelect["Drag and Drop / Select File"]
    ChooseMethod -->|"Sample Fixture"| SelectSample["Select Pre-loaded Sample"]
    
    DragSelect --> ValidateFile["Validate File Format and Size"]
    ValidateFile --> FileValid{"File Valid?"}
    FileValid -->|"No"| DisplayUploadError["Display Error and Remediation"]
    DisplayUploadError --> UploadScreen
    FileValid -->|"Yes"| ExtractText["Extract and Process Document Text"]
    
    SelectSample --> LoadSample["Load Sample Document"]
    LoadSample --> ExtractText
    
    ExtractText --> TextExtracted{"Text Extracted Successfully?"}
    TextExtracted -->|"No"| ShowExtractError["Show Extraction Error"]
    ShowExtractError --> ChangeSettings["Change Settings"]
    ChangeSettings --> UploadScreen
    
    TextExtracted -->|"Yes"| SaveDocMeta["Save Document and Metadata"]
    SaveDocMeta --> ShowPreview["Show Document Preview and Details"]
    ShowPreview --> ConfigScreen["Analysis Configuration Screen"]
    
    subgraph ConfigSection ["Analysis Configuration Screen"]
        ConfigAnalysis["Configure Analysis"] --> SelectDocType["Select Document Type"]
        SelectDocType --> ChooseSummaryStyle["Choose Summary Style"]
        ChooseSummaryStyle --> ChooseDepth["Choose Analysis Depth"]
        ChooseDepth --> SelectFocusTopics["Select Focus Topics"]
        SelectFocusTopics --> ClickAnalyze["Click Analyze Document"]
    end
    
    ConfigScreen --> ConfigAnalysis
    
    ClickAnalyze --> CheckCache{"Existing Cached Result?"}
    CheckCache -->|"Yes"| LoadCached["Load Cached Analysis"]
    CheckCache -->|"No"| GenAIAnalysis["Generate AI Analysis"]
    
    GenAIAnalysis --> AnalysisSuccess{"Analysis Successful?"}
    AnalysisSuccess -->|"No"| DisplayAnalysisError["Display Analysis Error"]
    DisplayAnalysisError --> ConfigScreen
    AnalysisSuccess -->|"Yes"| ValidateResults["Validate Structured Results"]
    ValidateResults --> CalcCompleteness["Calculate Completeness Score"]
    CalcCompleteness --> GenVisuals["Generate Charts and Visual Insights"]
    GenVisuals --> SaveAnalysisDB["Save Analysis to Database"]
    
    LoadCached --> ResultsDash
    SaveAnalysisDB --> ResultsDash
    
    subgraph ResultsDashboard ["Results Dashboard"]
        ViewDash["View Results Dashboard"]
        ReadSumm["Read Summary"]
        ExploreComp["Explore Completeness Score"]
        ViewStructured["View Structured Data and Raw JSON"]
        ExploreCharts["Explore Charts and Infographic"]
        ReviewMissing["Review Missing Fields and Warnings"]
        
        ViewDash --> ReadSumm
        ViewDash --> ExploreComp
        ViewDash --> ViewStructured
        ViewDash --> ExploreCharts
        ViewDash --> ReviewMissing
    end
    
    ResultsDash["Results Dashboard"] --> NextAction{"Next Action"}
    
    NextAction -->|"View Another Analysis"| ChooseHistory["Choose Analysis History"]
    ChooseHistory --> ResultsDash
    
    NextAction -->|"Copy or Export"| CopyExport["Copy Summary or JSON"]
    
    NextAction -->|"Delete Document"| ConfirmDelete["Confirm Deletion"]
    ConfirmDelete --> DeletionConfirmed{"Deletion Confirmed?"}
    DeletionConfirmed -->|"Yes"| DeleteDoc["Delete Document and Related Analyses"]
    DeleteDoc --> ReturnUpload["Return to Upload Screen"]
    ReturnUpload --> UploadScreen
    DeletionConfirmed -->|"No"| ResultsDash
    
    NextAction -->|"Finish"| EndNode([End])
```

---

## 🛠️ Technologies & Frameworks Used

### **Backend**
- **Language**: Python 3.11+ (Compatible with Python 3.11, 3.12, 3.14)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous, OpenAPI/Swagger auto-docs)
- **Web Server**: [Uvicorn](https://www.uvicorn.org/) (High-performance ASGI server)
- **Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **PDF Extraction**: [pdfplumber](https://github.com/jsvine/pdfplumber) (table-aware layout parser) & [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/) (high-speed fallback)
- **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) with `psycopg2-binary` (PostgreSQL) and native `sqlite3`
- **HTTP Client**: [HTTPX](https://www.python-httpx.org/) (Async HTTP requests)
- **File Management**: `aiofiles` and `python-multipart`

### **Frontend**
- **Framework**: [Nuxt 3](https://nuxt.com/) (Vue 3 + Vite, SSR-ready)
- **Language**: TypeScript & Modern ESNext
- **Styling**: Handcrafted Modern CSS Design System (Dark mode, glassmorphism, responsive grid, zero bulky CSS frameworks)
- **Icons**: [Lucide Icons](https://lucide.dev/) (Lightweight, SVG-based)
- **Visuals & Delighters**: [canvas-confetti](https://www.npmjs.com/package/canvas-confetti) for $\ge 80\%$ completeness celebrations, custom SVG donut charts, timelines, and grouped bar visualizations

---

## 🤖 AI Models, APIs & Services Used

| Component / Service | Technology / Provider | Purpose |
|---|---|---|
| **Primary LLM** | **Google Gemini 2.5 Flash** (`gemini-2.5-flash`) | Document entity extraction, synthesis, and JSON-structured output |
| **API Provider** | **Google AI Studio** | Free-tier access (15 requests/min, 1,500 requests/day) |
| **Deterministic Mock LLM** | In-house Python rule-based engine | High-fidelity zero-cost offline fallback if API key is absent or quota is reached |
| **Primary Database** | **Neon Cloud PostgreSQL** | Serverless production PostgreSQL storing document files and analysis records |
| **Backup Database** | **Local SQLite (`docuintel.db`)** | Automatic, zero-configuration local fallback if PostgreSQL connection drops |
| **Infographic Engine** | Server-side SVG Generator (`app.services.infographic_generator`) | Generates responsive SVG visual summary cards with document-tailored palettes and download capability |
| **Cloud Hosting** | **Render** (Backend) & **Vercel** (Frontend) | Production deployment with global CDN and automated CI/CD git triggers |

---

## 🔐 Required Environment Variables

> [!NOTE]
> All secret values are excluded. Configure these in `backend/.env` and `frontend/.env` (or via your cloud hosting dashboard).

### **Backend Variables (`backend/.env`)**

| Variable Name | Required? | Default Value | Description |
|---|:---:|:---:|---|
| `GEMINI_API_KEY` | Optional | `None` | Google Gemini API key from [Google AI Studio](https://aistudio.google.com/). If omitted, system seamlessly runs in **Mock Mode**. |
| `GEMINI_MODEL` | Optional | `gemini-2.5-flash` | Specific Gemini model tag to invoke for document reasoning. |
| `LLM_MODE` | Optional | `gemini` | Operating mode: `gemini` (live API call) or `mock` (instant deterministic response). |
| `DATABASE_URL` | Optional | `None` | PostgreSQL connection string (e.g., `postgresql://user:password@ep-xyz.neon.tech/docuintel?sslmode=require`). If omitted or invalid, auto-switches to SQLite. |
| `HOST` | Optional | `0.0.0.0` | Host IP address to bind the Uvicorn server. |
| `PORT` | Optional | `8000` | Port number for the backend server. |
| `CORS_ORIGINS` | Optional | `*` | Allowed CORS origins (comma-separated or `*` for all). |
| `MAX_UPLOAD_SIZE_MB` | Optional | `10` | Maximum allowable document upload file size in megabytes. |
| `ALLOWED_MIME_TYPES` | Optional | `application/pdf,text/plain,...` | Comma-delimited list of accepted MIME types. |
| `UPLOAD_DIR` | Optional | `uploads` | Local directory path where uploaded files are stored. |

### **Frontend Variables (`frontend/.env`)**

| Variable Name | Required? | Default Value | Description |
|---|:---:|:---:|---|
| `NUXT_PUBLIC_API_BASE` | **Required in Prod** | `http://127.0.0.1:8000/api/v1` | Base URL of the backend API (set to Render URL in production). |

---

## 📁 Repository Folder Structure

```
DocuIntel-AI-Platform/
├── Candidate_details.txt            # Candidate metadata and submission links
├── README.md                        # Master architectural documentation and user guide
├── Rishikesh_Resume.pdf             # Candidate resume
├── implementation_plan.md           # Implementation blueprint and scoring matrix
├── walkthrough.md                   # Visual verification and test walkthrough
│
├── backend/                         # FastAPI Application Root
│   ├── .env.example                 # Template for backend environment variables
│   ├── Dockerfile                   # Container definition for containerized deployment
│   ├── requirements.txt             # Python dependencies (FastAPI, PyMuPDF, SQLAlchemy, etc.)
│   ├── docuintel.db                 # Local SQLite failover database (auto-created)
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                # Pydantic BaseSettings environment loader
│   │   ├── main.py                  # FastAPI app entry point, CORS, and health probe
│   │   │
│   │   ├── db/                      # Two-Tier Database Layer
│   │   │   ├── connection.py        # PostgreSQL probe + SQLite automatic fallback engine
│   │   │   ├── crud.py              # CRUD operations for Documents and Analyses
│   │   │   └── models.py            # SQLAlchemy Declarative Models (DocumentDB, AnalysisDB)
│   │   │
│   │   ├── routers/                 # REST API Endpoints
│   │   │   ├── documents.py         # Ingestion, sample loading, file uploads
│   │   │   └── analyze.py           # Analysis pipeline, caching, completeness, visuals
│   │   │
│   │   ├── schemas/                 # Strict Pydantic v2 Models
│   │   │   ├── extraction.py        # Resume, Research Paper, and Business Report schemas
│   │   │   └── requests.py          # Request payloads, RFC 7807 error models, visual schemas
│   │   │
│   │   └── services/                # Business Logic Engines
│   │       ├── extractor.py         # Multi-stage PDF/TXT parsing & text normalization
│   │       ├── llm_service.py       # Prompt compiler, Gemini 2.5 client & mock engine
│   │       ├── completeness.py      # Weighted multi-dimensional completeness mathematics
│   │       ├── visual_service.py    # Domain chart aggregator (ECharts-ready)
│   │       └── infographic_generator.py # Server-side SVG infographic generator
│   │
│   ├── database/
│   │   └── schema.sql               # PostgreSQL DDL table definitions
│   │
│   ├── samples/                     # 6 Pre-Seeded Evaluation Documents
│   │   ├── sample_resume_standard.pdf / .txt
│   │   ├── sample_resume_missing_fields.pdf / .txt
│   │   ├── sample_research_paper.pdf / .txt
│   │   ├── sample_business_report.pdf / .txt
│   │   └── sample_empty.pdf / .txt
│   │
│   ├── tests/
│   │   └── test_api.py              # 12 automated integration tests (pytest)
│   │
│   └── uploads/                     # Stored document filesystem files
│
└── frontend/                        # Nuxt 3 (Vue 3) Web Application
    ├── .env.example                 # Template for frontend environment variables
    ├── nuxt.config.ts               # Nuxt build, meta tags, and runtime config
    ├── package.json                 # Node dependencies (Vue 3, Lucide, Canvas-Confetti)
    ├── app.vue                      # Root Vue template
    │
    ├── assets/
    │   └── css/
    │       └── main.css             # Glassmorphism design system & token definitions
    │
    ├── components/                  # Reusable Vue 3 Components
    │   ├── Navbar.vue               # Header, health status pill (Gemini 2.5), API Docs link
    │   ├── DocumentUploader.vue     # Drag-and-drop zone + 6 one-click sample cards
    │   ├── AdaptiveControls.vue     # Domain picker, style selector, depth, focus topics
    │   ├── CompletenessGauge.vue    # SVG circular progress gauge, warning flags, confetti
    │   ├── SummaryCard.vue          # Summary display, reading time, copy button
    │   ├── StructuredDataViewer.vue # Polymorphic Clean Cards + Raw JSON Viewer
    │   ├── VisualInsightsPanel.vue  # Domain SVG charts + SVG Infographic download
    │   └── ApiKeyModal.vue          # Interactive Gemini API key configuration modal
    │
    ├── composables/
    │   └── useApiUrl.ts             # Centralized API route resolver
    │
    └── pages/
        └── index.vue                # Main orchestrator dashboard page
```

---

## 🚀 Setup & Execution Instructions

### **Prerequisites**
- **Python**: 3.11, 3.12, or 3.14 installed
- **Node.js**: v18.0.0 or higher (Node 20 LTS recommended)
- **Git**: Installed and configured

---

### **1. Local Backend Setup**

```bash
# Navigate to the backend directory
cd backend

# Create a Python virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows (PowerShell / CMD):
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install all required Python packages
pip install -r requirements.txt

# Configure your environment file
copy .env.example .env   # On macOS/Linux use: cp .env.example .env

# (Optional) Open .env in your editor to add your GEMINI_API_KEY and DATABASE_URL
# If no GEMINI_API_KEY is provided, the platform automatically runs in deterministic Mock Mode!

# Launch the FastAPI development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend is now running at:
- **API Base**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Health Check Endpoint**: `http://127.0.0.1:8000/api/v1/health`

---

### **2. Local Frontend Setup**

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment file
copy .env.example .env   # On macOS/Linux use: cp .env.example .env

# Launch the Nuxt 3 development server
npm run dev
```

The frontend web application is now running at:
- **Web App**: `http://127.0.0.1:3000`

---

### **3. Production Deployment**

#### **Backend on Render (Web Service)**
1. Connect your GitHub repository to [Render](https://render.com/).
2. Select **Root Directory**: `backend`.
3. Set **Build Command**: `pip install -r requirements.txt`.
4. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. In **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google AI Studio key)*
   - `GEMINI_MODEL`: `gemini-2.5-flash`
   - `DATABASE_URL`: *(Your Neon PostgreSQL connection string)*
   - `LLM_MODE`: `gemini`

#### **Frontend on Vercel**
1. Import your GitHub repository into [Vercel](https://vercel.com/).
2. Select **Root Directory**: `frontend`.
3. Framework Preset: **Nuxt.js**.
4. In **Environment Variables**, add:
   - `NUXT_PUBLIC_API_BASE`: `https://<your-render-app>.onrender.com/api/v1`
5. Click **Deploy**.

---

## 🧪 Instructions for Testing Main Features

### **A. Automated Testing (Pytest Suite)**

Run the comprehensive automated test suite from the backend directory:

```bash
cd backend
python -m pytest tests/ -v
```

**12 out of 12 tests will execute and pass:**
1. `test_health_check`: Validates system status, database probe, and LLM configuration.
2. `test_list_samples`: Confirms all 6 pre-seeded sample fixtures are accessible.
3. `test_load_sample_success`: Tests loading and text extraction from sample files.
4. `test_load_empty_document_error_handling`: Verifies RFC 7807 422 error response when an empty/blank PDF is loaded.
5. `test_analyze_resume`: Tests standard resume extraction, skill parsing, and completeness calculation.
6. `test_analyze_missing_fields_resume`: Tests uncertainty flags and null handling for missing email/phone.
7. `test_analyze_research_paper`: Validates methodology, contributions, and benchmark metric extraction.
8. `test_analyze_business_report`: Validates financial KPIs, segment revenue shares, and risk extraction.
9. `test_pseudo_null_coercion`: Verifies conversion of `"N/A"`, `"none"`, and `"unknown"` strings into `None`.
10. `test_text_cleaning_pipeline`: Verifies NFKC normalization, de-hyphenation, and whitespace cleanup.
11. `test_upload_storage_in_filesystem_and_database`: Verifies file saving to `uploads/` and metadata insertion into the database.
12. `test_database_failover_to_sqlite_backup`: Validates immediate, non-crashing failover to SQLite when PostgreSQL is unavailable.

---

### **B. Manual Feature Walkthrough (Web UI)**

1. **Test Pre-Seeded Sample Fixtures**:
   - Open the web application at `http://127.0.0.1:3000` (or the [Live Demo](https://document-intelligence-frontend-two.vercel.app)).
   - In the **Quick Test Samples** grid, click **"Sarah Chen - Senior Full-Stack Engineer"**.
   - Notice the document instantly loads, displaying character count, file size, and line count.
2. **Configure Adaptive Controls**:
   - Select **Summary Style**: `Executive Brief`, `Detailed Synthesis`, or `Bullet Points`.
   - Select **Analysis Depth**: `Standard` or `Exhaustive`.
   - Select **Focus Topics**: Toggle badges like `Skills`, `Experience`, or `Education`.
   - Click **"Analyze Document"**.
3. **Inspect Completeness & Confetti**:
   - Observe the circular **Completeness Score Gauge** calculating $C_{\text{total}}$.
   - For complete documents ($\ge 80\%$), a celebratory confetti burst triggers!
4. **Test Incomplete Document & Uncertainty Warnings**:
   - Click the sample fixture **"Alex Rivera - Incomplete Entry-Level Resume"**.
   - Click **"Analyze Document"**.
   - Notice the completeness score drops ($\sim 50\%$) and the **Uncertainty & Missing Fields** alert card clearly flags missing phone number, certifications, and experience.
5. **Explore Structured Extraction (Clean vs Raw)**:
   - Switch between the **"Clean Cards"** view (human-friendly cards) and **"Raw JSON"** view.
   - Use the real-time search box to filter JSON keys, or click **"Download JSON"**.
6. **Test Visual Insights & Infographics**:
   - Switch to the **Visual Insights** panel.
   - Under **Domain Visualizations**, view the interactive SVG Skills Donut and Career Progression Timeline.
   - Under **AI Visual Summary**, view the dynamically synthesized SVG infographic card and click **"Download"** to save the vector graphic.
7. **Test Error Handling (Blank Document)**:
   - Click **"Empty / Blank Document"** and attempt analysis.
   - Observe the RFC 7807 compliant error banner providing clear diagnosis and remediation instructions.
8. **Test LLM Provider Modal**:
   - Click the **"LLM Config"** button in the navbar to input a custom Gemini API key or view the deterministic Mock Mode details.

---

## ⚠️ Known Limitations & Future Scope

| Limitation | Current Behavior | Production Recommendation / Future Scope |
|---|---|---|
| **Scanned / Handwritten Image OCR** | Currently extracts digital text streams via `pdfplumber` and `PyMuPDF`. Image-only/scanned PDFs produce an empty extraction warning. | Integrate an asynchronous OCR service like **Tesseract OCR**, **AWS Textract**, or **Google Cloud Vision** for rasterized scans. |
| **Multi-Tenant Authentication & RBAC** | Single-tenant public architecture without user accounts or permission layers. | Integrate **Clerk**, **Auth0**, or FastAPI OAuth2 with JWT tokens for multi-user document isolation and workspace sharing. |
| **Asynchronous Task Queue for Batch Jobs** | Document analysis executes synchronously per HTTP request. Large multi-hundred-page PDFs may hit browser gateway timeouts. | Introduce **Celery / Redis** or **Temporal** background workers with WebSocket-based progress streaming for large document batches. |
| **Distributed LLM Rate Limiting** | Gemini free-tier (15 RPM) is protected by in-memory SHA-256 caching and mock fallback, but lacks distributed queuing across multiple server replicas. | Deploy a Redis-backed distributed Token Bucket or Leaky Bucket queue to pace requests smoothly during traffic spikes. |

---


