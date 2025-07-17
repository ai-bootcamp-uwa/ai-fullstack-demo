"""
Main entry point for Backend Gateway API.
This file maintains compatibility while using the new organized structure.
"""

from src.api.main import app

if __name__ == "__main__":
    import uvicorn
    from src.core.config import settings
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug) 