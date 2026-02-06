"""
Health check endpoints for the QLR Generator API.
"""

import logging

from fastapi import APIRouter

from ...create_qlr.constants import HEALTH_RESPONSE

logger = logging.getLogger(__name__)

# Create router for health endpoints
router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Check the health status of the QLR Generator API. Returns service status and version.",
    responses={
        200: {
            "description": "Service is healthy and running",
            "content": {"application/json": {"example": {"status": "healthy", "version": "0.1.0"}}},
        }
    },
)
async def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify API service status.

    Returns the current health status and version of the QLR Generator API.
    """
    return HEALTH_RESPONSE
