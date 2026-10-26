"""
AI-Powered Document Intelligence Platform — FastAPI Application
Main entry point with CORS, database initialization, health endpoint, and router mounting.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.db.connection import get_active_backend_name, is_using_sqlite_backup
from app.routers import analyze, documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan: DB Initialization
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes database tables and storage directories."""
    logger.info("Initializing database tables...")
    init_db()
    yield
    logger.info("Application shutdown complete.")


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI-Powered Document Intelligence Platform",
    description=(
        "An interactive AI-powered document analysis application that extracts "
        "structured information from Resumes, Research Papers, and Business Analytics "
        "Reports. Generates summaries, visual insights, and adapts analysis based on "
        "user selections."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(documents.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Root & Health Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Root endpoint — API information."""
    return {
        "name": "AI-Powered Document Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "database_backend": get_active_backend_name(),
        "is_backup_database": is_using_sqlite_backup(),
        "file_storage": settings.UPLOAD_DIR,
    }


@app.get("/api/v1/health")
async def health():
    """
    Health check endpoint.
    Used by Render warmup pings and monitoring to verify LLM, DB, and storage state.
    """
    return {
        "status": "healthy",
        "llm_mode": settings.LLM_MODE,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "database_configured": bool(settings.DATABASE_URL),
        "database_backend": get_active_backend_name(),
        "is_backup_database": is_using_sqlite_backup(),
        "file_storage_dir": settings.UPLOAD_DIR,
    }


logger.info("Document Intelligence Platform API initialized")

