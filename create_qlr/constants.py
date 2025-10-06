"""
Constants and configuration values for QLR generation.

This module contains all hardcoded values, URLs, and configuration
that can be centralized for easier maintenance.
"""

# Template configuration
TEMPLATES_DIR = "templates"

# Error messages
ERROR_MESSAGES = {
    "TEMPLATE_NOT_FOUND": "Template file not found for collection: {collection}",
    "TEMPLATE_READ_ERROR": "Failed to read template file: {template_path}",
    "QLR_GENERATION_FAILED": "Failed to generate QLR XML from template",
}

# Success messages
SUCCESS_MESSAGES = {
    "QLR_CREATED": "QLR created successfully for STAC item {item_id} with collection {collection}",
}

# Logging configuration
LOG_FORMATS = {
    "INFO": "QLR generation for item {item_id} completed in {duration:.3f}s",
    "ERROR": "QLR generation failed for item {item_id}: {error}",
    "DEBUG": "Processing STAC item: {item_id} from collection: {collection}",
}


# Default values
DEFAULTS = {
    "LAYER_NAME_FALLBACK": "unknown_layer",
}
