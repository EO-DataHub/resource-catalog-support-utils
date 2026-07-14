"""
QLR (QGIS Layer) generation module.

This module provides functionality to create QLR files from STAC items,
handling template processing, URL extraction, and XML generation.
"""

import logging
from pathlib import Path
from typing import TypedDict
from urllib.parse import quote

from ..layer_generation.generation import create_document_from_request
from ..layer_generation.template_loader import generate_from_template
from .constants import DEFAULTS
from .models import QLRRequest

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = Path(__file__).parent / "templates" / "generic_template.xml"


class TemplateParams(TypedDict):
    """Type definition for template parameters used in QLR generation."""

    xyzUrl: str
    layer_id: str
    layer_name: str


def create_qlr_from_request(request: QLRRequest) -> str:
    """
    Create QLR file from a QLRRequest with xyzUrl information.

    This function uses the provided xyzUrl directly in the template, eliminating
    the need for collection-specific URL construction.

    Args:
        request: A QLRRequest object containing item and xyzUrl

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If QLR creation fails
        TemplateUnavailableError: If the QLR template file cannot be loaded
    """
    return create_document_from_request(request, "QLR", generate_qlr_from_xyz)


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
        TemplateUnavailableError: If the QLR template file cannot be loaded
    """
    if not layer_name:
        layer_name = DEFAULTS["LAYER_NAME_FALLBACK"]
    if not layer_id:
        layer_id = DEFAULTS["LAYER_NAME_FALLBACK"]

    def render(template: str) -> str:
        # Use proper URL encoding for specific characters - encode only the
        # characters that need encoding while preserving tile placeholders
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

    return generate_from_template(_TEMPLATE_PATH, "QLR", render)
