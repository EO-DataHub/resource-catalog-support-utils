"""
Application factory for the QLR Generator API.

This module creates and configures the FastAPI application instance,
wiring together all components including middleware, routes, and startup events.
"""

import logging
from fastapi import FastAPI
from create_qlr.template_cache import load_templates_at_startup
from create_qlr.constants import API_CONFIG
from middleware import setup_middleware
from routes import setup_routes

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
    app = FastAPI(
        title=API_CONFIG["title"],
        description=API_CONFIG["description"],
        version=API_CONFIG["version"],
        contact=API_CONFIG["contact"],
        license_info=API_CONFIG["license_info"],
    )

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
    default_config = API_CONFIG.copy()

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
