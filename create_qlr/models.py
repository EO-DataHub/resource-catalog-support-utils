"""
STAC (SpatioTemporal Asset Catalog) data models for QLR generation.

This module contains Pydantic models for validating and processing STAC items
received from the API.
"""

from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, validator, Field


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

    type: Literal[
        "Point",
        "LineString",
        "Polygon",
        "MultiPoint",
        "MultiLineString",
        "MultiPolygon",
    ]
    coordinates: Union[
        List[float],  # Point
        List[List[float]],  # LineString or MultiPoint
        List[List[List[float]]],  # Polygon or MultiLineString
        List[List[List[List[float]]]],  # MultiPolygon
    ]


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
    Complete STAC item with all required metadata.

    A STAC item is a GeoJSON Feature representing a spatiotemporal asset
    (satellite image, derived product, etc.) with metadata about what it is,
    when and where it was created, and how to access it.
    """

    type: Literal["Feature"] = Field(
        "Feature", description="GeoJSON Feature type - always 'Feature' for STAC items"
    )
    stac_version: str = Field(
        ...,
        description="Version of the STAC specification used (e.g., '1.0.0')",
        example="1.0.0",
    )
    stac_extensions: Optional[List[str]] = Field(
        [],
        description="List of STAC extensions used by this item",
        example=["proj", "eo"],
    )
    id: str = Field(
        ...,
        description="Unique identifier for the item within the collection",
        example="sentinel2-item-001",
    )
    collection: str = Field(
        ..., description="Collection this item belongs to", example="sentinel2_ard"
    )
    bbox: List[float] = Field(
        ...,
        description="Bounding box [minLon, minLat, maxLon, maxLat] in WGS84 coordinates",
        example=[-180, -90, 180, 90],
    )
    geometry: STACGeometry = Field(
        ..., description="Geometric footprint of the item as a GeoJSON geometry object"
    )
    properties: STACProperties = Field(
        ..., description="Additional properties and metadata for the item"
    )
    links: List[STACLink] = Field(
        ..., description="List of related links (self, parent, collection, etc.)"
    )
    assets: Dict[str, STACAsset] = Field(
        ...,
        description="Dictionary of assets (data files, thumbnails, metadata files, etc.)",
    )
    # Custom fields that might be added by the frontend
    tilesUrl: Optional[str] = Field(
        None,
        description="Custom field for tile service URL (optional, used by frontend)",
    )
    render: Optional[Dict[str, Any]] = Field(
        None, description="Custom rendering parameters (optional, used by frontend)"
    )


class QLRRequest(BaseModel):
    """
    Request payload for QLR file generation.

    Contains a STAC item, XYZ tile service URL, and render configuration ID
    needed to generate a QLR file for QGIS.
    """

    item: STACItem = Field(
        ...,
        description="Complete STAC item object containing metadata, geometry, and asset information",
        example={
            "type": "Feature",
            "stac_version": "1.0.0",
            "id": "sentinel2-item-001",
            "collection": "sentinel2_ard",
            "bbox": [-180, -90, 180, 90],
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]
                ],
            },
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "links": [],
            "assets": {},
        },
    )
    xyzUrl: str = Field(
        ...,
        description="Fully constructed XYZ tile service URL with all render parameters and placeholders",
        example="https://titiler.example.com/tiles/{z}/{x}/{y}?url=https://example.com/data.tif&bidx=1&bidx=2&bidx=3&resampling=bilinear",
    )
    renderId: str = Field(
        ...,
        description="Identifier for the render configuration being used (e.g., 'Natural Color', 'NDVI', 'False Color')",
        example="Natural Color",
    )

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
