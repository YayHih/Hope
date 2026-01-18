"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.routers import public


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


# Initialize rate limiter with Redis backend
# SECURITY FIX: Redis storage ensures rate limits are shared across all workers
# Without this, each worker has its own counter (allowing N× the limit with N workers)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL  # Shared rate limit storage across workers
)

app = FastAPI(
    title="Hope Platform API",
    description="NYC Homeless Services Platform - helping people find essential services",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CRITICAL SECURITY FIX: Trust Nginx to tell us the real client IP
# Without this, all traffic appears as 127.0.0.1 and rate limiting blocks EVERYONE
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(public.router, prefix="/api/v1/public", tags=["public"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hope Platform API",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }
