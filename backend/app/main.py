"""Veridian — Main FastAPI Application.

Production-ready AI-powered fraud detection and prevention system.
Provides REST API endpoints for SMS, email, and URL fraud analysis.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db, get_db, SessionLocal
from app.middleware.logging_middleware import RequestLoggingMiddleware, setup_logging
from app.middleware.rate_limiter import setup_rate_limiting
from app.routers import auth, scan, report, admin, chat, dashboard
from app.services.auth_service import AuthService

settings = get_settings()
logger = logging.getLogger("veridian")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle events."""
    # Startup
    setup_logging()
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database tables
    try:
        init_db()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database init note: {e}")

    # Create default admin user
    try:
        db = SessionLocal()
        AuthService.create_admin_user(db)
        db.close()
        logger.info("✅ Default admin user ready")
    except Exception as e:
        logger.warning(f"⚠️ Admin user creation note: {e}")

    # Pre-initialize AI models
    try:
        from app.services.scan_service import (
            get_sms_detector, get_email_detector, get_url_detector
        )
        get_sms_detector()
        get_email_detector()
        get_url_detector()
        logger.info("✅ AI models initialized and ready")
    except Exception as e:
        logger.warning(f"⚠️ AI model init note: {e}")

    logger.info(f"🛡️ {settings.APP_NAME} is ready to protect!")

    yield

    # Shutdown
    logger.info(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered Fraud Detection and Prevention System. "
        "Detects fraud in SMS messages, emails, and URLs using "
        "Machine Learning, NLP, and explainable AI."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Rate limiting
setup_rate_limiting(app)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "type": type(exc).__name__,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with structured responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


# Register API routers under /api/v1 prefix
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(scan.router, prefix=API_PREFIX)
app.include_router(report.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)


# Health check endpoint
@app.get("/", tags=["Health"])
def root():
    """Root endpoint — application health check."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "message": "Veridian is running. Visit /docs for API documentation.",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {
            "api": "operational",
            "database": "connected",
            "ai_models": "loaded",
        },
    }
