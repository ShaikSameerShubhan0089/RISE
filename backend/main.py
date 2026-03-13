"""
FastAPI Main Application
RISE - Risk Identification System for Early Detection
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="RISE API",
    description="RISE - Risk Identification System for Early Detection - Clinical Decision Support System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add audit logging middleware
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    return await log_request(request, call_next)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }


# Clinical disclaimer endpoint
@app.get("/api/disclaimer")
async def get_disclaimer():
    """Get clinical disclaimer text"""
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

# Serve SPA static files (frontend build)
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": str(type(exc).__name__)
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and load ML models on startup"""
    print("=" * 60)
    print("Starting RISE API")
    print("Risk Identification System for Early Detection")
    print("=" * 60)
    
    # Check database connection
    if check_db_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
    
    print(f"✓ API server ready")
    print(f"  Docs: http://localhost:8000/api/docs")
    print("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down CDSS API...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_RELOAD", "True").lower() == "true"
    )
