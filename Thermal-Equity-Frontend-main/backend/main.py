from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure project root and backend directory are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database.mongodb import MongoDBManager

try:
    from database.db import init_db
except ImportError:
    try:
        from db import init_db
    except ImportError:
        def init_db():
            pass

from backend.routes.auth_routes import router as auth_router
from backend.routes.api import router as api_router


def is_production() -> bool:
    return os.getenv("REQUIRE_MONGODB", "").strip().lower() == "true" or bool(os.getenv("PORT"))


def get_cors_origins() -> list[str]:
    configured = os.getenv("FRONTEND_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    origins.extend([
        "https://thermal-ai-main.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ])
    return list(dict.fromkeys(origins))


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await MongoDBManager.connect_to_database()
    except Exception as exc:
        if is_production():
            raise RuntimeError(
                "MongoDB startup connection failed; verify MONGODB_URI, "
                "DATABASE_NAME, and Atlas Network Access."
            ) from exc
        print(f"MongoDB unavailable; authentication requests will return 503: {type(exc).__name__}")

    # Initialize the local relational store only for local development.
    try:
        init_db()
    except Exception as exc:
        print(f"Local telemetry store initialization failed: {exc}")

    yield

    # Cleanup on shutdown
    try:
        await MongoDBManager.close_database_connection()
    except Exception:
        pass


app = FastAPI(
    title="Thermal Equity AI API",
    version="2.0.0",
    description="Urban thermal equity intelligence, MongoDB Atlas telemetry, and AI mitigation assessment API for Greater Chennai Corporation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth_router)
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request data",
            "errors": exception.errors(),
        },
    )


@app.get("/", tags=["Health"])
def home():
    return {
        "message": "Thermal Equity AI backend is working!",
        "version": "2.0.0",
        "status": "online",
        "mongodb_connected": MongoDBManager.is_connected(),
        "database": "MongoDB Atlas" if MongoDBManager.is_connected() else "Local Resilient Telemetry Store",
        "database_name": os.getenv("DATABASE_NAME", "thermal_equity"),
        "docs": "/docs",
        "endpoints": {
            "auth_register": "/api/auth/register",
            "auth_login": "/api/auth/login",
            "auth_me": "/api/auth/me",
            "health": "/api/health",
            "dashboard_summary": "/api/dashboard/summary",
            "locations": "/api/locations",
            "alerts": "/api/alerts",
            "ai_insights": "/api/ai/insights",
            "ai_recommendations": "/api/ai/recommendations",
            "predict": "/api/predict",
        },
    }


@app.get("/health", tags=["Health"], operation_id="health")
@app.get("/api/health", tags=["Health"], operation_id="api_health")
def health():
    is_connected = MongoDBManager.is_connected()
    return {
        "status": "ok",
        "service": "Thermal Equity AI API",
        "database": "MongoDB Atlas" if is_connected else "Local Resilient Telemetry Store",
        "database_name": os.getenv("DATABASE_NAME", "thermal_equity"),
        "mongodb_connected": is_connected,
        "region": "Greater Chennai Corporation (8 Monitored Wards)",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0" if os.getenv("PORT") else "127.0.0.1")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
    )