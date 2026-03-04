"""
Application configuration using Pydantic Settings.

This module provides centralized configuration management with environment variable
support, validation, and type safety.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class APIConfig(BaseModel):
    """API configuration settings."""

    title: str = "Resource Catalog Support Utils API"
    version: str = "0.2.0"
    description: str = """
    Resource catalog support utilities for STAC-based workflows.
    
    This API provides services for working with resource catalogs, including:
    - Generating QLR (QGIS Layer) files from STAC items with XYZ tile service URLs
    - Launching parameterized Jupyter notebooks from templates for STAC-based analysis
    
    Key features include template-based generation, frontend-controlled rendering, and template caching.
    
    Use cases: Load satellite imagery in QGIS, visualize geospatial data, launch analysis notebooks, integrate with STAC catalogs.
    """
    contact_name: str = "Resource Catalog Support API"
    contact_email: str = "support@example.com"
    license_name: str = "MIT License"
    license_url: str = "https://opensource.org/licenses/MIT"


class CORSConfig(BaseModel):
    """CORS configuration settings."""

    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "https://eodatahub.org.uk",
            "https://test.eodatahub.org.uk",
            "https://eodhrc.sparkgeo.dev",
            "https://develop.eodhrc.sparkgeo.dev",
            "https://staging.eodatahub.org.uk",
            "https://netlify.eodh.sparkgeo.dev",
        ],
        description="List of allowed CORS origins",
    )
    allow_credentials: bool = True
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    level: str = "INFO"
    log_requests: bool = True
    log_request_body: bool = False
    body_log_limit: int = 500


class HTTPConfig(BaseModel):
    """HTTP configuration settings."""

    methods_to_log_body: List[str] = Field(
        default_factory=lambda: ["POST", "PUT", "PATCH"]
    )
    timing_header: str = "X-Process-Time"


class Settings(BaseSettings):
    """Main application settings."""

    # API Configuration
    api: APIConfig = Field(default_factory=APIConfig)

    # CORS Configuration
    cors: CORSConfig = Field(default_factory=CORSConfig)

    # Logging Configuration
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # HTTP Configuration
    http: HTTPConfig = Field(default_factory=HTTPConfig)

    # Notebook Launch / JupyterHub Configuration
    jupyterhub_base_url: str = Field(
        default="https://eodatahub-workspaces.org.uk/notebooks",
        description="Base URL for the JupyterHub instance used to spawn notebooks",
    )
    notebook_s3_bucket: str = Field(
        default="workspaces-eodhp",
        description="S3 bucket for workspace notebooks",
    )

    # Environment
    environment: str = Field(default="dev", description="Deployment environment")

    # CORS Origins (can be overridden via environment variable)
    allowed_origins_env: Optional[str] = Field(
        default=None,
        alias="ALLOWED_ORIGINS",
        description="Comma-separated list of allowed origins",
    )

    # Logging settings (can be overridden via environment variables)
    log_level_env: Optional[str] = Field(
        default=None, alias="LOG_LEVEL", description="Log level override"
    )

    log_requests_env: Optional[str] = Field(
        default=None, alias="LOG_REQUESTS", description="Enable/disable request logging"
    )

    log_request_body_env: Optional[str] = Field(
        default=None,
        alias="LOG_REQUEST_BODY",
        description="Enable/disable request body logging",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("cors", always=True)
    def update_cors_origins(cls, v, values):
        """Update CORS origins from environment variable if provided."""
        allowed_origins_env = values.get("allowed_origins_env")
        if allowed_origins_env:
            # Split comma-separated values and strip whitespace
            origins = [
                origin.strip()
                for origin in allowed_origins_env.split(",")
                if origin.strip()
            ]
            # Filter out '*' when allow_credentials is True (not allowed by CORS spec)
            # Also filter out '*' to prevent duplicate headers
            if v.allow_credentials:
                origins = [origin for origin in origins if origin != "*"]
            # Remove any duplicates
            seen = set()
            unique_origins = []
            for origin in origins:
                if origin not in seen:
                    seen.add(origin)
                    unique_origins.append(origin)
            v.allowed_origins = unique_origins
        # Also ensure default origins don't include '*' when credentials are enabled
        elif v.allow_credentials and "*" in v.allowed_origins:
            v.allowed_origins = [
                origin for origin in v.allowed_origins if origin != "*"
            ]
        return v

    @validator("logging", always=True)
    def update_logging_config(cls, v, values):
        """Update logging configuration from environment variables if provided."""
        log_level_env = values.get("log_level_env")
        if log_level_env:
            v.level = log_level_env.upper()

        log_requests_env = values.get("log_requests_env")
        if log_requests_env:
            v.log_requests = log_requests_env.lower() in ("true", "1", "yes", "on")

        log_request_body_env = values.get("log_request_body_env")
        if log_request_body_env:
            v.log_request_body = log_request_body_env.lower() in (
                "true",
                "1",
                "yes",
                "on",
            )

        return v

    def get_fastapi_config(self) -> dict:
        """Get FastAPI configuration dictionary."""
        return {
            "title": self.api.title,
            "description": self.api.description,
            "version": self.api.version,
            "contact": {
                "name": self.api.contact_name,
                "email": self.api.contact_email,
            },
            "license_info": {
                "name": self.api.license_name,
                "url": self.api.license_url,
            },
        }

    def get_health_response(self) -> dict:
        """Get health check response."""
        return {
            "status": "healthy",
            "version": self.api.version,
            "environment": self.environment,
            "notebook_s3_bucket": self.notebook_s3_bucket,
        }


# Global settings instance
settings = Settings()


# Backward compatibility constants for existing code
class Constants:
    """Backward compatibility constants."""

    # API Configuration
    API_CONFIG = settings.get_fastapi_config()

    # CORS Configuration
    CORS_CONFIG = {
        "default_origins": ",".join(settings.cors.allowed_origins),
        "allow_credentials": settings.cors.allow_credentials,
        "allow_methods": settings.cors.allow_methods,
        "allow_headers": settings.cors.allow_headers,
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
        "log_level": settings.logging.level,
        "log_requests": str(settings.logging.log_requests).lower(),
        "log_request_body": str(settings.logging.log_request_body).lower(),
        "allowed_origins": ",".join(settings.cors.allowed_origins),
    }

    # HTTP Configuration
    HTTP_CONFIG = {
        "methods_to_log_body": settings.http.methods_to_log_body,
        "body_log_limit": settings.logging.body_log_limit,
        "timing_header": settings.http.timing_header,
    }

    # Status Emojis for Logging
    STATUS_EMOJIS = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
    }

    # Health Check Response
    HEALTH_RESPONSE = settings.get_health_response()

    # Service Information
    SERVICE_INFO = {
        "service": "Resource Catalog Support Utils",
        "version": settings.api.version,
        "description": "Provides QLR file generation and notebook launch services for STAC-based workflows",
        "capabilities": [
            "STAC item processing",
            "XYZ tile URL handling",
            "QLR file generation",
            "Notebook launch and parameterization",
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


# Export constants for backward compatibility
API_CONFIG = Constants.API_CONFIG
CORS_CONFIG = Constants.CORS_CONFIG
ENV_VARS = Constants.ENV_VARS
ENV_DEFAULTS = Constants.ENV_DEFAULTS
HTTP_CONFIG = Constants.HTTP_CONFIG
STATUS_EMOJIS = Constants.STATUS_EMOJIS
HEALTH_RESPONSE = Constants.HEALTH_RESPONSE
SERVICE_INFO = Constants.SERVICE_INFO
VALIDATION_MESSAGES = Constants.VALIDATION_MESSAGES
ERROR_MESSAGES = Constants.ERROR_MESSAGES
DEFAULTS = Constants.DEFAULTS
