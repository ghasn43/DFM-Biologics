"""
FastAPI application entry point.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="DFM Biologics API",
    description="SAFE in-silico construct builder and manufacturability gate for biologics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routes
from api.routes import router

app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": "DFM Biologics",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "score": "POST /score",
            "blueprint": "POST /blueprint"
        },
        "safety_notice": "This tool is for computational planning only. No wet-lab instructions provided."
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"\n🧬 DFM Biologics Backend")
    print(f"🚀 Starting on {host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level
    )
