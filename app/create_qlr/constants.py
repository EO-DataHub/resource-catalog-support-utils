"""
Constants and configuration values for QLR generation.

This module re-exports constants from the centralized settings configuration
for backward compatibility with existing code.
"""

# Import constants from centralized settings
from ..core.config import (
    API_CONFIG,
    CORS_CONFIG,
    ENV_VARS,
    ENV_DEFAULTS,
    HTTP_CONFIG,
    STATUS_EMOJIS,
    HEALTH_RESPONSE,
    SERVICE_INFO,
    VALIDATION_MESSAGES,
    ERROR_MESSAGES,
    DEFAULTS,
)

# Template configuration
TEMPLATES_DIR = "templates"
