"""
Main API routes configuration for the Resource Catalog Support Utils API.

This module sets up the main API routes and includes versioned API endpoints.
"""

from fastapi import FastAPI

from .v1 import health, lyrx, notebooks, qlr


def setup_routes(app: FastAPI) -> None:
    """
    Set up all API routes for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Include API v1 routes
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(qlr.router, prefix="/api/v1", tags=["QLR Generation"])
    app.include_router(lyrx.router, prefix="/api/v1", tags=["LYRX Generation"])
    app.include_router(notebooks.router, prefix="/api/v1", tags=["Notebook Launch"])

    # Keep backward compatibility with direct routes, hidden from the OpenAPI
    # schema so the platform docs aggregator doesn't list each endpoint twice
    app.include_router(health.router, tags=["Health"], include_in_schema=False)
    app.include_router(qlr.router, tags=["QLR Generation"], include_in_schema=False)
    app.include_router(lyrx.router, tags=["LYRX Generation"], include_in_schema=False)
    app.include_router(notebooks.router, tags=["Notebook Launch"], include_in_schema=False)
