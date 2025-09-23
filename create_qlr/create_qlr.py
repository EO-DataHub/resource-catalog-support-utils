"""
QLR (QGIS Layer) generation module.

This module provides functionality to create QLR files from STAC items,
handling template processing, URL extraction, and XML generation.
"""

from create_qlr.get_template import get_template_path
from create_qlr.models import STACItem
from create_qlr.constants import (
    TITILER_BASE_URL,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
    URL_PATTERNS,
    DEFAULTS,
    LOG_FORMATS,
)
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import unquote

logger = logging.getLogger(__name__)


def get_layer_id(url: str) -> str:
    """
    Extract a layer ID from a STAC item URL.

    This function attempts to extract the item ID from various URL formats,
    with fallback mechanisms for different URL structures.

    Args:
        url: The STAC item URL to extract the ID from

    Returns:
        The extracted layer/item ID

    Raises:
        ValueError: If the URL is invalid or no ID can be extracted
    """
    if not url or not url.strip():
        raise ValueError(ERROR_MESSAGES["INVALID_URL"])

    try:
        # Decode the URL first (it may be double-encoded)
        decoded_url = unquote(url.strip())

        # Extract the item ID from the URL path
        # The URL structure is: .../items/{item_id}
        if URL_PATTERNS["ITEMS_PATH"] in decoded_url:
            item_id = (
                decoded_url.split(URL_PATTERNS["ITEMS_PATH"])[-1]
                .split(URL_PATTERNS["QUERY_SEPARATOR"])[0]
                .split(URL_PATTERNS["PARAM_SEPARATOR"])[0]
            )
            if item_id:
                logger.debug(
                    SUCCESS_MESSAGES["LAYER_ID_EXTRACTED"].format(layer_id=item_id)
                )
                return item_id

        # Fallback: use the last part of the URL as ID
        fallback_id = decoded_url.rstrip("/").split("/")[-1]
        if fallback_id:
            logger.warning(f"Using fallback ID extraction for URL: {url}")
            return fallback_id

        raise ValueError(ERROR_MESSAGES["MISSING_ITEM_ID"].format(url=url))

    except Exception as e:
        logger.error(f"Failed to extract layer ID from URL {url}: {e}")
        raise ValueError(ERROR_MESSAGES["MISSING_ITEM_ID"].format(url=url))


def generate_qlr(
    url: str,
    layer_id: str,
    layer_name: Optional[str] = None,
    template_path: Optional[str] = None,
    stac_item: Optional[Dict[str, Any]] = None,
    titiler_base_url: Optional[str] = None,
) -> str:
    """
    Generate QLR XML from metadata and template.

    This function takes a template file and fills it with the provided parameters
    to create a complete QLR XML file.

    Args:
        url: The data source URL
        layer_id: Unique identifier for the layer
        layer_name: Human-readable name for the layer
        template_path: Path to the QLR template file
        stac_item: Dictionary containing STAC item metadata
        titiler_base_url: Base URL for the Titiler service

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If template path is invalid or QLR generation fails
        FileNotFoundError: If template file cannot be found
    """
    if not template_path:
        raise ValueError("Template path is required")

    if not Path(template_path).exists():
        raise ValueError(
            ERROR_MESSAGES["TEMPLATE_NOT_FOUND"].format(collection="unknown")
        )

    if layer_name is None:
        layer_name = os.path.basename(url) or DEFAULTS["LAYER_NAME_FALLBACK"]

    try:
        with open(template_path, "r") as f:
            template = f.read()

        # Base template parameters
        template_params: Dict[str, Any] = {
            "datasource": url,
            "layer_id": layer_id,
            "layer_name": layer_name,
            "titiler_base_url": titiler_base_url or TITILER_BASE_URL,
        }

        # Add STAC item metadata if available
        if stac_item:
            # Add bounding box coordinates
            if (
                "bbox" in stac_item
                and isinstance(stac_item["bbox"], list)
                and len(stac_item["bbox"]) == 4
            ):
                bbox = stac_item["bbox"]
                template_params.update(
                    {
                        "xmin": bbox[0],
                        "ymin": bbox[1],
                        "xmax": bbox[2],
                        "ymax": bbox[3],
                        "wgs84_xmin": bbox[0],
                        "wgs84_ymin": bbox[1],
                        "wgs84_xmax": bbox[2],
                        "wgs84_ymax": bbox[3],
                    }
                )
            else:
                logger.warning("Invalid or missing bounding box in STAC item")

            # Add CRS information if available
            if (
                "properties" in stac_item
                and isinstance(stac_item["properties"], dict)
                and "proj:epsg" in stac_item["properties"]
            ):
                epsg_code = stac_item["properties"]["proj:epsg"]
                template_params.update(
                    {
                        "crs_epsg": epsg_code,
                        "crs_wkt": DEFAULTS["CRS_WKT"],
                        "crs_proj4": DEFAULTS["CRS_PROJ4"],
                    }
                )

        qlr_xml = template.format(**template_params)
        logger.info(f"Successfully generated QLR for {url}")
        return qlr_xml

    except FileNotFoundError:
        error_msg = ERROR_MESSAGES["TEMPLATE_READ_ERROR"].format(
            template_path=template_path
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    except KeyError as e:
        error_msg = f"Missing template parameter: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = ERROR_MESSAGES["QLR_GENERATION_FAILED"]
        logger.error(f"{error_msg}: {e}")
        raise ValueError(f"{error_msg}: {str(e)}")


def create_qlr(
    url: str, collection: str, stac_item: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create QLR file for given URL and collection with proper error handling.

    This is the main function for creating QLR files from STAC items.
    It validates inputs, retrieves the appropriate template, and generates
    the complete QLR XML.

    Args:
        url: The data source URL (typically a STAC item self-link)
        collection: The collection name (e.g., 'sentinel2_ard')
        stac_item: Optional dictionary containing STAC item metadata

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If inputs are invalid or QLR creation fails
    """
    try:
        # Validate inputs
        if not url or not url.strip():
            raise ValueError(ERROR_MESSAGES["INVALID_URL"])

        if not collection or not collection.strip():
            raise ValueError(ERROR_MESSAGES["INVALID_COLLECTION"])

        # Get template path
        template_path = get_template_path(collection.strip())

        # Generate QLR
        layer_name = get_layer_id(url)
        qlr = generate_qlr(
            url=url,
            layer_name=layer_name,
            layer_id=layer_name,
            template_path=template_path,
            stac_item=stac_item,
            titiler_base_url=TITILER_BASE_URL,
        )

        logger.info(f"QLR created successfully for {url} with collection {collection}")
        return qlr

    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        logger.error(f"QLR creation failed: {e}")
        raise ValueError(f"Unexpected error during QLR creation: {str(e)}")


def create_qlr_from_stac(item: STACItem) -> str:
    """
    Create QLR file from a validated STAC item.

    This function extracts the self-link from a STAC item and creates
    a QLR file using the item's metadata and collection information.

    Args:
        item: A validated STACItem object containing all required metadata

    Returns:
        Complete QLR XML as a string

    Raises:
        ValueError: If STAC item is missing required fields or QLR creation fails
    """
    try:
        logger.debug(
            LOG_FORMATS["DEBUG"].format(item_id=item.id, collection=item.collection)
        )

        # Find the self link
        self_link = next((link for link in item.links if link.rel == "self"), None)
        if not self_link:
            raise ValueError(ERROR_MESSAGES["MISSING_SELF_LINK"])

        # Create QLR using the generated URL and collection
        qlr_xml = create_qlr(self_link.href, item.collection, item.dict())

        logger.info(
            SUCCESS_MESSAGES["QLR_CREATED"].format(
                item_id=item.id, collection=item.collection
            )
        )

        return qlr_xml

    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        logger.error(
            LOG_FORMATS["ERROR"].format(
                item_id=getattr(item, "id", "unknown"), error=str(e)
            )
        )
        raise ValueError(f"Failed to create QLR from STAC item: {str(e)}")
