"""
LYRX (ArcGIS Layer) generation module.

This module provides functionality to create LYRX files from STAC items,
handling template processing, URL extraction, and CIM JSON generation.
"""

import json
import logging
from pathlib import Path
from string import Template

from ..layer_generation.generation import create_document_from_request
from ..layer_generation.template_loader import generate_from_template
from .constants import DEFAULTS
from .models import LYRXRequest

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = Path(__file__).parent / "templates" / "generic_template.lyrx"


def create_lyrx_from_request(request: LYRXRequest) -> str:
    """
    Create LYRX file from a LYRXRequest with xyzUrl information.

    This function uses the provided xyzUrl directly in the template, eliminating
    the need for collection-specific URL construction.

    Args:
        request: A LYRXRequest object containing item and xyzUrl

    Returns:
        Complete LYRX (CIM) JSON as a string

    Raises:
        ValueError: If LYRX creation fails
        TemplateUnavailableError: If the LYRX template file cannot be loaded
    """
    return create_document_from_request(request, "LYRX", generate_lyrx_from_xyz)


def _as_json_string_literal(value: str) -> str:
    """Escape a value for safe embedding inside a JSON string literal."""
    return json.dumps(value)[1:-1]


def generate_lyrx_from_xyz(
    xyz_url: str,
    layer_id: str,
    layer_name: str,
) -> str:
    """
    Generate LYRX (CIM) JSON from xyzUrl and metadata using a template file.

    This function loads the template directly from disk and fills it
    with the provided parameters to create a complete LYRX file.

    ArcGIS Pro's tiled service layer accepts the {z}/{x}/{y} tile-coordinate
    placeholders verbatim, so the xyzUrl is embedded unmodified.

    Args:
        xyz_url: The fully constructed XYZ tile service URL
        layer_id: Unique identifier for the layer
        layer_name: Human-readable name for the layer

    Returns:
        Complete LYRX JSON as a string

    Raises:
        ValueError: If LYRX generation fails
        TemplateUnavailableError: If the template file is not found or cannot be read
    """
    if not layer_name:
        layer_name = DEFAULTS["LAYER_NAME_FALLBACK"]
    if not layer_id:
        layer_id = DEFAULTS["LAYER_NAME_FALLBACK"]

    def render(template: str) -> str:
        substitutions = {
            "XYZ_URL": _as_json_string_literal(xyz_url),
            "LAYER_ID": _as_json_string_literal(layer_id),
            "LAYER_NAME": _as_json_string_literal(layer_name),
        }
        lyrx_json = Template(template).substitute(substitutions)
        logger.info(f"Successfully generated LYRX for {layer_id} using direct template loading")
        return lyrx_json

    return generate_from_template(_TEMPLATE_PATH, "LYRX", render)
