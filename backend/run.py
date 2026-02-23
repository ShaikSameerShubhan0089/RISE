"""
Backend Server Startup Script
Run this to start the FastAPI development server
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv # Added import for load_dotenv

# Ensure project root is in path for ml module and other imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

# Load environment variables explicitly
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path, override=True)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Starting Autism Risk Stratification CDSS API Server")
    print("=" * 60)
    
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("API_RELOAD", "True").lower() == "true"
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"API Docs: http://localhost:{port}/api/docs")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
