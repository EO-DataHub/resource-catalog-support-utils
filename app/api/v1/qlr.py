"""
QLR generation endpoints for the QLR Generator API.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from ...create_qlr.models import QLRRequest
from ...create_qlr.constants import ERROR_MESSAGES
from ...services.qlr_service import QLRService

logger = logging.getLogger(__name__)

# Create router for QLR endpoints
router = APIRouter()

# Initialize business logic service
qlr_service = QLRService()


@router.post(
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
