"""
FastAPI Main Application
Autism Risk Stratification CDSS Backend + Frontend
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in path for ml module
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

load_dotenv()

from database import engine, Base, check_db_connection
from middleware.audit import log_request

# Import routers
from routers import auth, children, assessments, predictions, referrals, interventions, dashboard

# Create FastAPI app
app = FastAPI(
    title="Autism Risk Stratification CDSS API",
    description="Clinical Decision Support System for Early Autism Risk Stratification",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# -----------------------------
# CORS Configuration
# -----------------------------
# Read from .env
cors_origins_env = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # must match frontend domain(s)
    allow_credentials=True,       # allow cookies
    allow_methods=["*"],          # GET, POST, etc.
    allow_headers=["*"],          # Authorization, Content-Type, etc.
)

# -----------------------------
# Audit Logging Middleware
# -----------------------------
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    return await log_request(request, call_next)

# -----------------------------
# API Endpoints
# -----------------------------
@app.get("/api/health")
async def health_check():
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }

@app.get("/api/disclaimer")
async def get_disclaimer():
    return {
        "disclaimer": (
            "This tool provides autism risk stratification based on structured "
            "developmental assessments. It does NOT provide a clinical diagnosis. "
            "Final diagnosis must be made by a qualified pediatrician or "
            "developmental specialist."
        )
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(children.router, prefix="/api/children", tags=["Children"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Risk Predictions"])
app.include_router(referrals.router, prefix="/api/referrals", tags=["Referrals"])
app.include_router(interventions.router, prefix="/api/interventions", tags=["Interventions"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# -----------------------------
# Serve React Frontend
# -----------------------------
STATIC_DIR = backend_dir / "static"

if STATIC_DIR.exists():

    # Serve static assets (Vite build)
    if (STATIC_DIR / "assets").exists():
        app.mount(
            "/assets",
            StaticFiles(directory=STATIC_DIR / "assets"),
            name="assets"
        )

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """
        Serve React SPA for all non-API routes
        """
        # Prevent overriding API routes
        if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        file_path = STATIC_DIR / full_path

        # If file exists, serve it
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html (SPA fallback)
        return FileResponse(STATIC_DIR / "index.html")

# -----------------------------
# Global Exception Handler
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"ERROR: Exception during {request.method} {request.url.path}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": str(type(exc).__name__),
            "error": str(exc)
        }
    )

# -----------------------------
# Startup Event
# -----------------------------
@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("Starting Autism Risk Stratification CDSS API")
    print("=" * 60)

    if check_db_connection():
        print("[OK] Database connection successful")
    else:
        print("[FAIL] Database connection failed")

    print("[OK] API server ready")
    print("Docs available at: /api/docs")
    print("=" * 60)

# -----------------------------
# Shutdown Event
# -----------------------------
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down CDSS API...")

# -----------------------------
# Local Development Run
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_RELOAD", "True").lower() == "true"
    )
