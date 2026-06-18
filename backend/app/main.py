import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth
from app.core.config import get_settings
from app.core.database import check_database_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": request.url.path,
        },
    )


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    db_healthy = await check_database_connection()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "version": "1.0.0",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.on_event("startup")
async def startup_event():
    db_ok = await check_database_connection()
    if db_ok:
        logger.info("Database connection established")
    else:
        logger.warning("Database connection failed on startup")


@app.get("/")
async def root():
    return {
        "message": "Project Task Management API",
        "docs": "/docs" if settings.DEBUG else None,
    }