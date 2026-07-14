"""
LYRX generation endpoints for the Resource Catalog Support Utils API.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from ...create_lyrx.constants import DEFAULTS, ERROR_MESSAGES
from ...create_lyrx.create_lyrx import create_lyrx_from_request
from ...create_lyrx.models import LYRXRequest
from ...layer_generation.filename import safe_filename_component
from ...layer_generation.template_loader import TemplateUnavailableError

logger = logging.getLogger(__name__)

# Create router for LYRX endpoints
router = APIRouter()


@router.post(
    "/lyrx",
    summary="Generate LYRX File",
    description="""
    Generate an ArcGIS layer (LYRX) file from a STAC item and XYZ tile service URL.

    Creates a LYRX file that can be opened directly in ArcGIS Pro to load the same
    pre-rendered tile layer QGIS users get from the QLR endpoint. Requires a complete
    STAC item object and a fully constructed XYZ tile URL.
    Returns a CIM JSON file with .lyrx extension for use in ArcGIS Pro.
    """,
    responses={
        200: {
            "description": "LYRX file generated successfully",
            "content": {
                "application/json": {
                    "example": (
                        "{\n"
                        '  "type": "CIMLayerDocument",\n'
                        '  "version": "3.1.0",\n'
                        '  "build": 41833,\n'
                        '  "layers": ["CIMPATH=Map/example-item.json"],\n'
                        '  "layerDefinitions": [\n'
                        "    {\n"
                        '      "type": "CIMTiledServiceLayer",\n'
                        '      "name": "Example Layer",\n'
                        '      "serviceConnection": {\n'
                        '        "type": "CIMStandardServiceConnection",\n'
                        '        "serviceType": "1",\n'
                        '        "url": "https://example.com/tiles/{z}/{x}/{y}"\n'
                        "      }\n"
                        "    }\n"
                        "  ]\n"
                        "}"
                    )
                }
            },
            "headers": {
                "Content-Disposition": {
                    "description": "Filename for the downloaded LYRX file",
                    "schema": {
                        "type": "string",
                        "example": 'attachment; filename="example-item.lyrx"',
                    },
                }
            },
        },
        400: {
            "description": "Bad Request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "xyzUrl must contain {z}, {x}, and {y} placeholders for tile coordinates"}
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {"application/json": {"example": {"detail": "Internal server error"}}},
        },
    },
)
async def create_lyrx_endpoint(request: LYRXRequest) -> Response:
    """
    Generate a LYRX file from a STAC item and XYZ tile service URL.

    Processes a STAC item and XYZ URL to create a LYRX file for ArcGIS Pro.
    Validates input, extracts metadata, and returns the LYRX file as a
    downloadable attachment.
    """
    try:
        lyrx_json = create_lyrx_from_request(request)

        # Use item ID for filename, sanitized and falling back to a default when empty
        filename_id = safe_filename_component(request.item.id) or DEFAULTS["LAYER_NAME_FALLBACK"]
        output_filename = f"{filename_id}.lyrx"

        return Response(
            content=lyrx_json,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{output_filename}"'},
        )
    except TemplateUnavailableError as e:
        logger.error(f"LYRX template unavailable: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES["internal_server_error"],
        ) from e
    except ValueError as e:
        logger.error(f"LYRX generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error during LYRX generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES["internal_server_error"],
        ) from e
