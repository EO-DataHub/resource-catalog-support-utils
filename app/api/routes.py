"""
Main API routes configuration for the Resource Catalog Support Utils API.

This module sets up the main API routes and includes versioned API endpoints.
"""

from fastapi import FastAPI

from .v1 import health, notebooks, qlr


def setup_routes(app: FastAPI) -> None:
    """
    Set up all API routes for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Include API v1 routes
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(qlr.router, prefix="/api/v1", tags=["QLR Generation"])
    app.include_router(notebooks.router, prefix="/api/v1", tags=["Notebook Launch"])

    # Keep backward compatibility with direct routes
    app.include_router(health.router, tags=["Health"])
    app.include_router(qlr.router, tags=["QLR Generation"])
    app.include_router(notebooks.router, tags=["Notebook Launch"])
