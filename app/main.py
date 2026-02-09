"""
Main entry point for the QLR Generator API.

This module creates and configures the FastAPI application using the modular structure.
"""

import logging
from .app_factory import create_app
from .core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.logging.level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI application using the factory
app = create_app()

# Export the app for uvicorn and other ASGI servers
__all__ = ["app"]
