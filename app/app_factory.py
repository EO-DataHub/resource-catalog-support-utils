"""
Application factory for the QLR Generator API.

This module creates and configures the FastAPI application instance,
wiring together all components including middleware, routes, and startup events.
"""

import logging
from fastapi import FastAPI
from .create_qlr.template_cache import load_templates_at_startup
from .core.config import settings
from .core.middleware import setup_middleware
from .api.routes import setup_routes

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This factory function creates a new FastAPI instance and configures
    all middleware, routes, and startup events.

    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI application
    app = FastAPI(**settings.get_fastapi_config())

    # Set up middleware
    setup_middleware(app)

    # Set up routes
    setup_routes(app)

    # Set up startup event
    @app.on_event("startup")
    async def startup_event():
        """Load templates at application startup for better performance."""
        logger.info("Starting up application...")
        try:
            load_templates_at_startup()
            logger.info("Application startup completed successfully")
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise

    logger.info("FastAPI application created and configured successfully")
    return app


def create_app_with_config(**kwargs) -> FastAPI:
    """
    Create FastAPI application with custom configuration.

    Args:
        **kwargs: Additional configuration options for FastAPI

    Returns:
        Configured FastAPI application instance
    """
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

    # Set up startup event
    @app.on_event("startup")
    async def startup_event():
        """Load templates at application startup for better performance."""
        logger.info("Starting up application...")
        try:
            load_templates_at_startup()
            logger.info("Application startup completed successfully")
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise

    logger.info("FastAPI application created with custom configuration")
    return app
