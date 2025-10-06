"""
QLR (QGIS Layer) generation module.

This module provides functionality to create QLR files from STAC items,
handling template processing, URL extraction, and XML generation.
"""

import os
from create_qlr.models import QLRRequest
from create_qlr.constants import (
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
    DEFAULTS,
    LOG_FORMATS,
)
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def create_qlr_from_request(request: QLRRequest) -> str:
    """
    Create QLR file from a QLRRequest with xyzUrl and render information.

    This function uses the provided xyzUrl directly in the template, eliminating
    the need for collection-specific URL construction.

    Args:
        request: A QLRRequest object containing item, xyzUrl, and renderId

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If QLR creation fails
    """
    try:
        logger.debug(
            LOG_FORMATS["DEBUG"].format(
                item_id=request.item.id, collection=request.item.collection
            )
        )

        # Get the generic template path directly
        template_path = os.path.join(
            os.path.dirname(__file__), "templates", "generic_template.xml"
        )

        # Extract layer name from STAC item properties
        layer_name = request.item.id
        if hasattr(request.item.properties, "title") and request.item.properties.title:
            layer_name = request.item.properties.title
        elif hasattr(request.item.properties, "name") and request.item.properties.name:
            layer_name = request.item.properties.name

        # Generate QLR using the xyzUrl directly
        qlr_xml = generate_qlr_from_xyz(
            xyz_url=request.xyzUrl,
            layer_id=request.item.id,
            layer_name=layer_name,
            template_path=template_path,
        )

        logger.info(
            SUCCESS_MESSAGES["QLR_CREATED"].format(
                item_id=request.item.id, collection=request.item.collection
            )
        )

        return qlr_xml

    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        logger.error(
            LOG_FORMATS["ERROR"].format(
                item_id=getattr(request.item, "id", "unknown"), error=str(e)
            )
        )
        raise ValueError(f"Failed to create QLR from request: {str(e)}")


def generate_qlr_from_xyz(
    xyz_url: str,
    layer_id: str,
    layer_name: str,
    template_path: str,
) -> str:
    """
    Generate QLR XML from xyzUrl and metadata using a template.

    This function takes a template file and fills it with the provided parameters
    to create a complete QLR XML file using the xyzUrl directly.

    Args:
        xyz_url: The fully constructed XYZ tile service URL
        layer_id: Unique identifier for the layer
        layer_name: Human-readable name for the layer
        template_path: Path to the QLR template file

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If template path is invalid or QLR generation fails
        FileNotFoundError: If template file cannot be found
    """
    if not template_path:
        raise ValueError("Template path is required")

    if not os.path.exists(template_path):
        raise ValueError(
            ERROR_MESSAGES["TEMPLATE_NOT_FOUND"].format(collection="default")
        )

    if not layer_name:
        layer_name = DEFAULTS["LAYER_NAME_FALLBACK"]

    try:
        with open(template_path, "r") as f:
            template = f.read()

        # Template parameters - selectively encode only the parts that need encoding
        # Don't encode the entire URL, just the query parameters and placeholders
        # This matches the working format from normal.qlr
        url_encoded_xyz_url = (
            xyz_url.replace("{z}", "%7Bz%7D")
            .replace("{x}", "%7Bx%7D")
            .replace("{y}", "%7By%7D")
            .replace("&", "%26")
        )

        template_params: Dict[str, Any] = {
            "xyzUrl": url_encoded_xyz_url,
            "layer_id": layer_id,
            "layer_name": layer_name,
        }

        qlr_xml = template.format(**template_params)
        logger.info(f"Successfully generated QLR for {layer_id} using xyzUrl")
        return qlr_xml

    except FileNotFoundError:
        error_msg = ERROR_MESSAGES["TEMPLATE_READ_ERROR"].format(
            template_path=template_path
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    except KeyError as e:
        error_msg = f"Missing template parameter: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = ERROR_MESSAGES["QLR_GENERATION_FAILED"]
        logger.error(f"{error_msg}: {e}")
        raise ValueError(f"{error_msg}: {str(e)}")
