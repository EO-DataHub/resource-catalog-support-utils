"""
Main entry point for the QLR Generator API.

This module creates and configures the FastAPI application using the modular structure.
"""

import os
import logging
from .app_factory import create_app
from .create_qlr.constants import ENV_VARS, ENV_DEFAULTS

# Configure logging
log_level = os.getenv(ENV_VARS["log_level"], ENV_DEFAULTS["log_level"]).upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI application using the factory
app = create_app()

# Export the app for uvicorn and other ASGI servers
__all__ = ["app"]