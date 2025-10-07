"""
API routes for the QLR Generator API.

This module contains all API endpoint definitions and their documentation.
"""

import logging
from typing import Dict
from fastapi import HTTPException, status
from fastapi.responses import Response
from create_qlr.models import QLRRequest
from create_qlr.constants import HEALTH_RESPONSE, ERROR_MESSAGES
from business_logic import QLRService

logger = logging.getLogger(__name__)

# Initialize business logic service
qlr_service = QLRService()


def setup_routes(app):
    """
    Set up all API routes for the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.get(
        "/health",
        summary="Health Check",
        description="Check the health status of the QLR Generator API. Returns service status and version.",
        responses={
            200: {
                "description": "Service is healthy and running",
                "content": {
                    "application/json": {
                        "example": {"status": "healthy", "version": "0.1.0"}
                    }
                },
            }
        },
        tags=["Health"],
    )
    async def health_check() -> Dict[str, str]:
        """
        Health check endpoint to verify API service status.

        Returns the current health status and version of the QLR Generator API.
        """
        return HEALTH_RESPONSE

    @app.post(
        "/qlr",
        summary="Generate QLR File",
        description="""
        Generate a QLR (QGIS Layer) file from a STAC item and XYZ tile service URL.
        
        Creates a QLR file that can be opened directly in QGIS to load geospatial data layers.
        Requires a complete STAC item object, fully constructed XYZ tile URL, and render ID.
        Returns an XML file with .qlr extension for use in QGIS.
        """,
        responses={
            200: {
                "description": "QLR file generated successfully",
                "content": {
                    "application/xml": {
                        "example": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE qgis-layer-definition>
<qlr>
  <layer-tree-group expanded="1" groupLayer="" name="" checked="Qt::Checked">
    <layer-tree-layer expanded="1" legend_split_behavior="0" 
                      source="http-header:referer=&amp;type=xyz&amp;url=https://example.com/tiles/{z}/{x}/{y}" 
                      id="example-item" name="Example Layer" providerKey="wms" 
                      checked="Qt::Checked">
    </layer-tree-layer>
  </layer-tree-group>
</qlr>"""
                    }
                },
                "headers": {
                    "Content-Disposition": {
                        "description": "Filename for the downloaded QLR file",
                        "schema": {
                            "type": "string",
                            "example": 'attachment; filename="example-item.qlr"',
                        },
                    }
                },
            },
            400: {
                "description": "Bad Request - Invalid input data",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "xyzUrl must contain {z}, {x}, and {y} placeholders for tile coordinates"
                        }
                    }
                },
            },
            500: {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {"example": {"detail": "Internal server error"}}
                },
            },
        },
        tags=["QLR Generation"],
    )
    async def create_qlr_endpoint(request: QLRRequest) -> Response:
        """
        Generate a QLR file from a STAC item and XYZ tile service URL.

        Processes a STAC item and XYZ URL to create a QLR file for QGIS.
        Validates input, extracts metadata, applies URL encoding, and returns
        the QLR file as a downloadable attachment.
        """
        try:
            # Use business logic service to generate QLR
            qlr_xml = qlr_service.generate_qlr(request)

            # Use item ID for filename
            output_filename = f"{request.item.id}.qlr"

            return Response(
                content=qlr_xml,
                media_type="application/xml",
                headers={
                    "Content-Disposition": f'attachment; filename="{output_filename}"'
                },
            )
        except ValueError as e:
            logger.error(f"QLR generation failed: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error during QLR generation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_MESSAGES["internal_server_error"],
            )

    logger.info("API routes configured successfully")
