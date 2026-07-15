"""
Business logic for QLR generation service.

This module contains the core business logic for QLR generation,
separated from routing and middleware concerns.
"""

import logging
from typing import Any

from ..create_qlr.constants import (
    SERVICE_INFO,
    VALIDATION_MESSAGES,
)
from ..create_qlr.create_qlr import create_qlr_from_request
from ..create_qlr.models import QLRRequest
from ..layer_generation.template_loader import TemplateUnavailableError

logger = logging.getLogger(__name__)


class QLRService:
    """
    Service class for QLR generation business logic.

    This class encapsulates all business logic related to QLR file generation,
    providing a clean interface for the API layer to interact with.
    """

    def __init__(self) -> None:
        """Initialize the QLR service."""
        logger.info("QLR service initialized")

    def generate_qlr(self, request: QLRRequest) -> str:
        """
        Generate a QLR file from a QLR request.

        This method handles the core business logic for QLR generation,
        including validation, processing, and error handling.

        Args:
            request: QLRRequest containing STAC item and XYZ URL

        Returns:
            QLR XML content as a string

        Raises:
            ValueError: If QLR generation fails due to invalid input
            TemplateUnavailableError: If the QLR template file cannot be loaded
        """
        try:
            logger.debug(f"Generating QLR for item: {request.item.id}")

            # Delegate to the existing QLR generation function
            qlr_xml = create_qlr_from_request(request)

            logger.info(f"Successfully generated QLR for item: {request.item.id}")
            return qlr_xml

        except ValueError as e:
            # Re-raise validation errors as-is
            logger.error(f"QLR generation validation error for item {request.item.id}: {e}")
            raise
        except TemplateUnavailableError:
            # Re-raise as-is; this is a server-side deployment fault, not a validation error
            raise
        except Exception as e:
            # Wrap unexpected errors with more context
            logger.error(f"Unexpected error generating QLR for item {request.item.id}: {e}")
            raise ValueError(f"{VALIDATION_MESSAGES['qlr_generation_failed']}: {e!s}") from e

    def get_service_info(self) -> dict[str, Any]:
        """
        Get information about the QLR service.

        Returns:
            Dictionary containing service information
        """
        return SERVICE_INFO
