"""
Shared request-processing flow for layer file generation (QLR, LYRX).
"""

import logging
from collections.abc import Callable

from .models import STACItem, XYZLayerRequest
from .template_loader import TemplateUnavailableError

logger = logging.getLogger(__name__)


def extract_layer_name(item: STACItem) -> str:
    """Extract a human-readable layer name from STAC item properties, falling back to the item id."""
    if item.properties.title:
        return item.properties.title
    if item.properties.name:
        return item.properties.name
    return item.id


def create_document_from_request(
    request: XYZLayerRequest,
    format_name: str,
    generate_document: Callable[..., str],
) -> str:
    """
    Run the shared request-processing flow around a format-specific document generator.

    Args:
        request: An XYZLayerRequest (QLRRequest or LYRXRequest) containing item and xyzUrl
        format_name: Human-readable format name for log messages (e.g. "QLR", "LYRX")
        generate_document: Format-specific generator, called with xyz_url/layer_id/layer_name kwargs

    Returns:
        The generated document content as a string

    Raises:
        ValueError: If document creation fails
        TemplateUnavailableError: If the template file cannot be loaded
    """
    try:
        logger.debug(f"Processing STAC item: {request.item.id} from collection: {request.item.collection}")

        layer_name = extract_layer_name(request.item)

        document = generate_document(
            xyz_url=request.xyzUrl,
            layer_id=request.item.id,
            layer_name=layer_name,
        )

        logger.info(
            f"{format_name} created successfully for STAC item {request.item.id} "
            f"with collection {request.item.collection}"
        )

        return document

    except ValueError:
        # Re-raise ValueError with original message
        raise
    except TemplateUnavailableError:
        # Re-raise as-is; this is a server-side deployment fault, not a validation error
        raise
    except Exception as e:
        logger.error(f"{format_name} generation failed for item {getattr(request.item, 'id', 'unknown')}: {e!s}")
        raise ValueError(f"Failed to create {format_name} from request: {e!s}") from e
