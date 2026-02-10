"""
QLR (QGIS Layer) generation module.

This module provides functionality to create QLR files from STAC items,
handling template processing, URL extraction, and XML generation.
"""

import logging
from pathlib import Path
from typing import TypedDict
from urllib.parse import quote

from .constants import (
    DEFAULTS,
)
from .models import QLRRequest

logger = logging.getLogger(__name__)


class TemplateParams(TypedDict):
    """Type definition for template parameters used in QLR generation."""

    xyzUrl: str
    layer_id: str
    layer_name: str


def load_template_directly(template_name: str = "generic") -> str:
    """
    Load template directly from file without caching.

    Args:
        template_name: Name of the template to load (default: "generic")

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template file doesn't exist
        IOError: If template file cannot be read
    """
    # Get the templates directory
    templates_dir = Path(__file__).parent / "templates"

    # Load the generic template
    template_path = templates_dir / f"{template_name}_template.xml"

    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    try:
        with open(template_path, encoding="utf-8") as f:
            template_content = f.read()

        logger.debug(f"Successfully loaded template: {template_name}")
        return template_content

    except OSError as e:
        logger.error(f"Failed to read template file {template_path}: {e}")
        raise OSError(f"Failed to read template file {template_path}: {e}") from e


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
        logger.debug(f"Processing STAC item: {request.item.id} from collection: {request.item.collection}")

        # Extract layer name from STAC item properties
        layer_name = request.item.id
        if request.item.properties.title:
            layer_name = request.item.properties.title
        elif request.item.properties.name:
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
        logger.error(f"QLR generation failed for item {getattr(request.item, 'id', 'unknown')}: {e!s}")
        raise ValueError(f"Failed to create QLR from request: {e!s}") from e


def generate_qlr_from_xyz(
    xyz_url: str,
    layer_id: str,
    layer_name: str,
) -> str:
    """
    Generate QLR XML from xyzUrl and metadata using a template file.

    This function loads the template directly from disk and fills it
    with the provided parameters to create a complete QLR XML file.

    Args:
        xyz_url: The fully constructed XYZ tile service URL
        layer_id: Unique identifier for the layer
        layer_name: Human-readable name for the layer

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If QLR generation fails
        FileNotFoundError: If template file is not found
        IOError: If template file cannot be read
    """
    if not layer_name:
        layer_name = DEFAULTS["LAYER_NAME_FALLBACK"]

    try:
        # Load template directly from file
        template = load_template_directly("generic")

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
        logger.info(f"Successfully generated QLR for {layer_id} using direct template loading")
        return qlr_xml

    except (OSError, FileNotFoundError) as e:
        error_msg = f"Failed to load template: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = "Failed to generate QLR XML from template"
        logger.error(f"{error_msg}: {e}")
        raise ValueError(f"{error_msg}: {e!s}") from e
