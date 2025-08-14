#!/usr/bin/env python3
"""
Script to run the FinRisk API server
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def main():
    """Run the FinRisk API server"""
    print("🚀 Starting FinRisk API Server...")
    
    # Set default configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"📍 Server will run on {host}:{port}")
    print(f"🔧 Debug mode: {reload}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"📖 ReDoc Documentation: http://{host}:{port}/redoc")
    print("")
    
    # Start the server
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
