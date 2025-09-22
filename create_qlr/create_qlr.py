from create_qlr.get_template import get_template_path
import os
import logging
from typing import Optional
from pathlib import Path
from urllib.parse import unquote

logger = logging.getLogger(__name__)


def get_layer_id(url: str) -> str:
    """
    Create a layer ID from the URL.
    """

    # Decode the URL first (it may be double-encoded)
    decoded_url = unquote(url)

    # Extract the item ID from the URL path
    # The URL structure is: .../items/{item_id}
    if "/items/" in decoded_url:
        item_id = decoded_url.split("/items/")[-1].split("&")[0].split("?")[0]
        return item_id
    else:
        # Fallback: use the last part of the URL as ID
        return decoded_url.rstrip("/").split("/")[-1]


def generate_qlr(
    url: str,
    layer_id: str,
    layer_name: Optional[str] = None,
    template_path: Optional[str] = None,
) -> str:
    """
    Generate QLR XML from metadata and template.
    """
    if not template_path or not Path(template_path).exists():
        raise ValueError("Template path is required and must exist")

    if layer_name is None:
        layer_name = os.path.basename(url)

    try:
        with open(template_path, "r") as f:
            template = f.read()

        qlr_xml = template.format(
            datasource=url,
            layer_id=layer_id,
            layer_name=layer_name,
        )

        logger.info(f"Successfully generated QLR for {url}")
        return qlr_xml

    except Exception as e:
        logger.error(f"Failed to generate QLR: {e}")
        raise ValueError(f"Error generating QLR: {str(e)}")


def create_qlr(url: str, collection: str) -> str:
    """
    Create QLR file for given URL and collection with proper error handling.
    """
    try:
        # Validate inputs
        if not url or not collection:
            raise ValueError("URL and collection are required")

        if not url.strip():
            raise ValueError("URL cannot be empty")

        if not collection.strip():
            raise ValueError("Collection cannot be empty")

        # Get template path
        template_path = get_template_path(collection.strip())

        # Generate QLR
        layer_name = get_layer_id(url)
        qlr = generate_qlr(
            url=url,
            layer_name=layer_name,
            layer_id=layer_name,
            template_path=template_path,
        )

        logger.info(f"QLR created successfully for {url} with collection {collection}")
        return qlr

    except Exception as e:
        logger.error(f"QLR creation failed: {e}")
        raise
