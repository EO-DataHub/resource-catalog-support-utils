"""
Constants and configuration values for QLR generation.

This module re-exports constants from the centralized settings configuration
for backward compatibility with existing code.
"""

# Import constants from centralized settings
from ..core.config import (
    API_CONFIG,
    CORS_CONFIG,
    DEFAULTS,
    ENV_DEFAULTS,
    ENV_VARS,
    ERROR_MESSAGES,
    HEALTH_RESPONSE,
    HTTP_CONFIG,
    SERVICE_INFO,
    STATUS_EMOJIS,
    VALIDATION_MESSAGES,
)

__all__ = [
    "API_CONFIG",
    "CORS_CONFIG",
    "DEFAULTS",
    "ENV_DEFAULTS",
    "ENV_VARS",
    "ERROR_MESSAGES",
    "HEALTH_RESPONSE",
    "HTTP_CONFIG",
    "SERVICE_INFO",
    "STATUS_EMOJIS",
    "TEMPLATES_DIR",
    "VALIDATION_MESSAGES",
]

# Template configuration
TEMPLATES_DIR = "templates"
