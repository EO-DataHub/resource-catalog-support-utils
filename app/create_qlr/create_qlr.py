"""
QLR (QGIS Layer) generation module.

This module provides functionality to create QLR files from STAC items,
handling template processing, URL extraction, and XML generation.
"""

from urllib.parse import quote
from .models import QLRRequest
from .constants import (
    DEFAULTS,
)
from .template_cache import get_cached_template
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)


class TemplateParams(TypedDict):
    """Type definition for template parameters used in QLR generation."""

    xyzUrl: str
    layer_id: str
    layer_name: str


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
            f"Processing STAC item: {request.item.id} from collection: {request.item.collection}"
        )

        # Extract layer name from STAC item properties
        layer_name = request.item.id
        if hasattr(request.item.properties, "title") and request.item.properties.title:
            layer_name = request.item.properties.title
        elif hasattr(request.item.properties, "name") and request.item.properties.name:
            layer_name = request.item.properties.name

        # Generate QLR using the xyzUrl directly with cached template
        qlr_xml = generate_qlr_from_xyz(
            xyz_url=request.xyzUrl,
            layer_id=request.item.id,
            layer_name=layer_name,
        )

        logger.info(
            f"QLR created successfully for STAC item {request.item.id} with collection {request.item.collection}"
        )

        return qlr_xml

    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        logger.error(
            f"QLR generation failed for item {getattr(request.item, 'id', 'unknown')}: {str(e)}"
        )
        raise ValueError(f"Failed to create QLR from request: {str(e)}")


def generate_qlr_from_xyz(
    xyz_url: str,
    layer_id: str,
    layer_name: str,
) -> str:
    """
    Generate QLR XML from xyzUrl and metadata using a cached template.

    This function uses a pre-loaded template from the template cache and fills it
    with the provided parameters to create a complete QLR XML file.

    Args:
        xyz_url: The fully constructed XYZ tile service URL
        layer_id: Unique identifier for the layer
        layer_name: Human-readable name for the layer

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If QLR generation fails
        KeyError: If template is not found in cache
    """
    if not layer_name:
        layer_name = DEFAULTS["LAYER_NAME_FALLBACK"]

    try:
        # Get template from cache instead of loading from disk
        template = get_cached_template("generic")

        # Template parameters - use proper URL encoding for specific characters
        # Encode only the characters that need encoding while preserving tile placeholders
        url_encoded_xyz_url = (
            xyz_url.replace("{z}", quote("{z}"))
            .replace("{x}", quote("{x}"))
            .replace("{y}", quote("{y}"))
            .replace("&", quote("&"))
        )

        template_params: TemplateParams = {
            "xyzUrl": url_encoded_xyz_url,
            "layer_id": layer_id,
            "layer_name": layer_name,
        }

        qlr_xml = template.format(**template_params)
        logger.info(f"Successfully generated QLR for {layer_id} using cached template")
        return qlr_xml

    except KeyError as e:
        if "not found in cache" in str(e):
            error_msg = "Template not found in cache. Application may not have started properly."
            logger.error(error_msg)
            raise ValueError(error_msg)
        else:
            error_msg = f"Missing template parameter: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        error_msg = "Failed to generate QLR XML from template"
        logger.error(f"{error_msg}: {e}")
        raise ValueError(f"{error_msg}: {str(e)}")