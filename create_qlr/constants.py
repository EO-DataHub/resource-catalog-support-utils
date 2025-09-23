"""
Constants and configuration values for QLR generation.

This module contains all hardcoded values, URLs, and configuration
that can be centralized for easier maintenance.
"""

import os

# Titiler service configuration
TITILER_BASE_URL = os.getenv(
    "TITILER_BASE_URL",
    "https://eodatahub.org.uk/titiler/core/stac/tiles/WebMercatorQuad/%7Bz%7D/%7Bx%7D/%7By%7D",
)

# Template configuration
TEMPLATES_DIR = "templates"
CONFIG_FILE = "template_config.json"

# Error messages
ERROR_MESSAGES = {
    "MISSING_SELF_LINK": "No self link found in STAC item - this is required for QLR generation",
    "INVALID_URL": "Invalid or empty URL provided",
    "INVALID_COLLECTION": "Invalid or empty collection provided",
    "TEMPLATE_NOT_FOUND": "Template file not found for collection: {collection}",
    "TEMPLATE_READ_ERROR": "Failed to read template file: {template_path}",
    "QLR_GENERATION_FAILED": "Failed to generate QLR XML from template",
    "MISSING_ITEM_ID": "Could not extract item ID from URL: {url}",
    "INVALID_BBOX": "Invalid bounding box format in STAC item",
    "MISSING_REQUIRED_FIELD": "Missing required field '{field}' in STAC item",
}

# Success messages
SUCCESS_MESSAGES = {
    "QLR_CREATED": "QLR created successfully for STAC item {item_id} with collection {collection}",
    "TEMPLATE_LOADED": "Template loaded successfully: {template_path}",
    "LAYER_ID_EXTRACTED": "Layer ID extracted from URL: {layer_id}",
}

# Logging configuration
LOG_FORMATS = {
    "INFO": "QLR generation for item {item_id} completed in {duration:.3f}s",
    "ERROR": "QLR generation failed for item {item_id}: {error}",
    "DEBUG": "Processing STAC item: {item_id} from collection: {collection}",
}

# URL patterns for extraction
URL_PATTERNS = {
    "ITEMS_PATH": "/items/",
    "QUERY_SEPARATOR": "&",
    "PARAM_SEPARATOR": "?",
}

# Default values
DEFAULTS = {
    "LAYER_NAME_FALLBACK": "unknown_layer",
    "CRS_WKT": "",
    "CRS_PROJ4": "",
    "EMPTY_STRING": "",
}
