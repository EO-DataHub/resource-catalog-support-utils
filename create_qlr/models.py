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

    @validator("collection")
    def validate_collection(cls, v: str) -> str:
        """
        Validate that collection is not empty or whitespace-only.

        Args:
            v: Collection string to validate

        Returns:
            Stripped collection string

        Raises:
            ValueError: If collection is empty or whitespace-only
        """
        if not v or not v.strip():
            raise ValueError("Collection cannot be empty or whitespace-only")
        return v.strip()

    @validator("bbox")
    def validate_bbox(cls, v: List[float]) -> List[float]:
        """
        Validate that bbox has exactly 4 coordinates.

        Args:
            v: Bounding box coordinates to validate

        Returns:
            Validated bounding box coordinates

        Raises:
            ValueError: If bbox doesn't have exactly 4 coordinates
        """
        if len(v) != 4:
            raise ValueError(
                "Bbox must have exactly 4 coordinates [minLon, minLat, maxLon, maxLat]"
            )
        return v
