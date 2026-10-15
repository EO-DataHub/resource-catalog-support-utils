"""
Application factory for the Resource Catalog Support Utils API.

This module creates and configures the FastAPI application instance,
wiring together all components including middleware and routes.
"""

import logging

from fastapi import FastAPI

from .api.routes import setup_routes
from .core.auth import AuthError, auth_error_handler, check_auth_configured
from .core.config import settings
from .core.middleware import setup_middleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This factory function creates a new FastAPI instance and configures
    all middleware and routes.

    Returns:
        Configured FastAPI application instance
    """
    check_auth_configured()

    # Create FastAPI application
    app = FastAPI(**settings.get_fastapi_config())

    # Set up middleware
    setup_middleware(app)

    # Set up routes
    setup_routes(app)
    app.add_exception_handler(AuthError, auth_error_handler)

    logger.info("FastAPI application created and configured successfully")
    return app


def create_app_with_config(**kwargs: str) -> FastAPI:
    """
    Create FastAPI application with custom configuration.

    Args:
        **kwargs: Additional configuration options for FastAPI

    Returns:
        Configured FastAPI application instance
    """
    check_auth_configured()

    # Default configuration
    default_config = settings.get_fastapi_config()

    # Merge with provided configuration
    config = {**default_config, **kwargs}

    # Create FastAPI application with custom config
    app = FastAPI(**config)

    # Set up middleware
    setup_middleware(app)

    # Set up routes
    setup_routes(app)
    app.add_exception_handler(AuthError, auth_error_handler)

    logger.info("FastAPI application created with custom configuration")
    return app
