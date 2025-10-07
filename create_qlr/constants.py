"""
Constants and configuration values for QLR generation.

This module contains all hardcoded values, URLs, and configuration
that can be centralized for easier maintenance.
"""

# Template configuration
TEMPLATES_DIR = "templates"

# API Configuration
API_CONFIG = {
    "title": "QLR Generator API",
    "version": "0.1.0",
    "description": """
    Generate QLR (QGIS Layer) files from STAC items with XYZ tile service URLs.
    
    This API creates QLR files that can be opened directly in QGIS to load geospatial data layers.
    Key features include template-based generation, frontend-controlled rendering, and template caching.
    
    Use cases: Load satellite imagery in QGIS, visualize geospatial data, integrate with STAC catalogs.
    """,
    "contact": {
        "name": "QLR Generator API Support",
        "email": "support@example.com",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
}

# CORS Configuration
CORS_CONFIG = {
    "default_origins": "http://127.0.0.1:5173,http://localhost:5173",
    "origin_regex": r"^https:\/\/([a-z0-9-]+\.)?(eodatahub\.org\.uk|eodhrc\.sparkgeo\.dev)$",
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Environment Variables
ENV_VARS = {
    "log_level": "LOG_LEVEL",
    "log_requests": "LOG_REQUESTS",
    "log_request_body": "LOG_REQUEST_BODY",
    "allowed_origins": "ALLOWED_ORIGINS",
}

# Default Environment Values
ENV_DEFAULTS = {
    "log_level": "INFO",
    "log_requests": "true",
    "log_request_body": "false",
    "allowed_origins": CORS_CONFIG["default_origins"],
}

# HTTP Configuration
HTTP_CONFIG = {
    "methods_to_log_body": ["POST", "PUT", "PATCH"],
    "body_log_limit": 500,
    "timing_header": "X-Process-Time",
}

# Status Emojis for Logging
STATUS_EMOJIS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
}

# Health Check Response
HEALTH_RESPONSE = {
    "status": "healthy",
    "version": API_CONFIG["version"],
}

# Service Information
SERVICE_INFO = {
    "service": "QLR Generator",
    "version": API_CONFIG["version"],
    "description": "Generates QLR files from STAC items and XYZ tile URLs",
    "capabilities": [
        "STAC item processing",
        "XYZ tile URL handling",
        "QLR file generation",
        "Template-based processing",
    ],
}

# Validation Messages
VALIDATION_MESSAGES = {
    "stac_item_required": "STAC item is required",
    "xyz_url_required": "XYZ URL is required",
    "render_id_required": "Render ID is required",
    "qlr_generation_failed": "Failed to generate QLR",
}

# Error Messages
ERROR_MESSAGES = {
    "internal_server_error": "Internal server error",
    "template_not_found": "Template not found in cache. Application may not have started properly.",
    "missing_template_parameter": "Missing template parameter",
    "failed_to_generate_qlr": "Failed to generate QLR XML from template",
}

# Default values
DEFAULTS = {
    "LAYER_NAME_FALLBACK": "unknown_layer",
    "unknown_client": "unknown",
    "unknown_user_agent": "unknown",
}
