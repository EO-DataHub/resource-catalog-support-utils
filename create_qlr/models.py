"""
STAC (SpatioTemporal Asset Catalog) data models for QLR generation.

This module contains Pydantic models for validating and processing STAC items
received from the API.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, validator


class STACAsset(BaseModel):
    """
    Represents a STAC asset with metadata about a data file.

    Attributes:
        href: URL or path to the asset
        roles: List of roles this asset serves (e.g., 'data', 'thumbnail')
        size: Size of the asset in bytes
        location: Geographic location of the asset
    """

    href: str
    roles: Optional[List[str]] = []
    size: Optional[int] = None
    location: Optional[str] = None


class STACLink(BaseModel):
    """
    Represents a link in a STAC item.

    Attributes:
        rel: Relationship type of the link (e.g., 'self', 'parent', 'root')
        type: MIME type of the linked resource
        href: URL of the linked resource
    """

    rel: str
    type: Optional[str] = None
    href: str


class STACGeometry(BaseModel):
    """
    Represents the geometric footprint of a STAC item.

    Attributes:
        type: Type of geometry (e.g., 'Polygon', 'Point')
        coordinates: Array of coordinate arrays defining the geometry
    """

    type: str
    coordinates: List[List[List[float]]]


class STACProperties(BaseModel):
    """
    Represents properties/metadata of a STAC item.

    Attributes:
        datetime: ISO 8601 datetime string
    """

    datetime: str

    # Allow additional properties
    class Config:
        extra = "allow"


class STACItem(BaseModel):
    """
    Represents a complete STAC item with all required metadata.

    Attributes:
        type: Always "Feature" for STAC items
        stac_version: Version of the STAC specification
        stac_extensions: List of STAC extensions used
        id: Unique identifier for the item
        collection: Collection this item belongs to
        bbox: Bounding box [minLon, minLat, maxLon, maxLat]
        geometry: Geometric footprint of the item
        properties: Additional properties/metadata
        links: List of related links
        assets: Dictionary of assets (data files)
        tilesUrl: Custom field for tile service URL
        render: Custom rendering parameters
    """

    type: str
    stac_version: str
    stac_extensions: Optional[List[str]] = []
    id: str
    collection: str
    bbox: List[float]
    geometry: STACGeometry
    properties: STACProperties
    links: List[STACLink]
    assets: Dict[str, STACAsset]
    # Custom fields that might be added by the frontend
    tilesUrl: Optional[str] = None
    render: Optional[Dict[str, Any]] = None


class QLRRequest(BaseModel):
    """
    Represents a QLR generation request with the new payload structure.

    Attributes:
        item: The STAC item object
        xyzUrl: The fully constructed XYZ tile service URL with all render parameters
        renderId: The ID of the render configuration being used
    """

    item: STACItem
    xyzUrl: str
    renderId: str

    @validator("xyzUrl")
    def validate_xyz_url(cls, v: str) -> str:
        """
        Validate that xyzUrl is not empty and appears to be a valid URL.

        Args:
            v: XYZ URL string to validate

        Returns:
            Validated XYZ URL string

        Raises:
            ValueError: If xyzUrl is empty or doesn't appear to be a valid URL
        """
        if not v or not v.strip():
            raise ValueError("xyzUrl cannot be empty")

        url = v.strip()
        if not url.startswith(("http://", "https://")):
            raise ValueError("xyzUrl must be a valid HTTP/HTTPS URL")

        if "{z}" not in url or "{x}" not in url or "{y}" not in url:
            raise ValueError(
                "xyzUrl must contain {z}, {x}, and {y} placeholders for tile coordinates"
            )

        return url

    @validator("renderId")
    def validate_render_id(cls, v: str) -> str:
        """
        Validate that renderId is not empty.

        Args:
            v: Render ID string to validate

        Returns:
            Validated render ID string

        Raises:
            ValueError: If renderId is empty or whitespace-only
        """
        if not v or not v.strip():
            raise ValueError("renderId cannot be empty or whitespace-only")
        return v.strip()
