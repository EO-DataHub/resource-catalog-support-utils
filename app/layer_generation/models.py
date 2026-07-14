"""
Shared STAC data models and base request model for layer file generation.

STACItem and its nested models describe the STAC item payload accepted by
both the QLR and LYRX generation endpoints. XYZLayerRequest is the common
request shape (STAC item + XYZ tile URL) that QLRRequest and LYRXRequest
each build on.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    roles: list[str] | None = []
    size: int | None = None
    location: str | None = None


class STACLink(BaseModel):
    """
    Represents a link in a STAC item.

    Attributes:
        rel: Relationship type of the link (e.g., 'self', 'parent', 'root')
        type: MIME type of the linked resource
        href: URL of the linked resource
    """

    rel: str
    type: str | None = None
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
    coordinates: (
        list[float]  # Point
        | list[list[float]]  # LineString or MultiPoint
        | list[list[list[float]]]  # Polygon or MultiLineString
        | list[list[list[list[float]]]]  # MultiPolygon
    )


class STACProperties(BaseModel):
    """
    Represents properties/metadata of a STAC item.

    Attributes:
        datetime: ISO 8601 datetime string
    """

    model_config = ConfigDict(extra="allow")

    datetime: str
    title: str | None = None
    name: str | None = None


class STACItem(BaseModel):
    """
    Complete STAC item with all required metadata.

    A STAC item is a GeoJSON Feature representing a spatiotemporal asset
    (satellite image, derived product, etc.) with metadata about what it is,
    when and where it was created, and how to access it.
    """

    type: Literal["Feature"] = Field("Feature", description="GeoJSON Feature type - always 'Feature' for STAC items")
    stac_version: str = Field(
        ...,
        description="Version of the STAC specification used (e.g., '1.0.0')",
    )
    stac_extensions: list[str] | None = Field(
        [],
        description="List of STAC extensions used by this item",
    )
    id: str = Field(
        ...,
        description="Unique identifier for the item within the collection",
    )
    collection: str = Field(..., description="Collection this item belongs to")
    bbox: list[float] = Field(
        ...,
        description="Bounding box [minLon, minLat, maxLon, maxLat] in WGS84 coordinates",
    )
    geometry: STACGeometry = Field(..., description="Geometric footprint of the item as a GeoJSON geometry object")
    properties: STACProperties = Field(..., description="Additional properties and metadata for the item")
    links: list[STACLink] = Field(..., description="List of related links (self, parent, collection, etc.)")
    assets: dict[str, STACAsset] = Field(
        ...,
        description="Dictionary of assets (data files, thumbnails, metadata files, etc.)",
    )
    # Custom fields that might be added by the frontend
    tilesUrl: str | None = Field(
        None,
        description="Custom field for tile service URL (optional, used by frontend)",
    )
    render: dict[str, Any] | None = Field(None, description="Custom rendering parameters (optional, used by frontend)")


class XYZLayerRequest(BaseModel):
    """
    Common request payload shape for layer file generation endpoints.

    Contains a STAC item and XYZ tile service URL, shared by both the QLR
    and LYRX request models.
    """

    item: STACItem = Field(
        ...,
        description="Complete STAC item object containing metadata, geometry, and asset information",
    )
    xyzUrl: str = Field(
        ...,
        description="Fully constructed XYZ tile service URL with all render parameters and placeholders",
    )

    @field_validator("xyzUrl")
    @classmethod
    def validate_xyz_url(cls, v: str) -> str:
        """Validate that xyzUrl is not empty and appears to be a valid URL."""
        if not v or not v.strip():
            raise ValueError("xyzUrl cannot be empty")

        url = v.strip()
        if not url.startswith(("http://", "https://")):
            raise ValueError("xyzUrl must be a valid HTTP/HTTPS URL")

        if "{z}" not in url or "{x}" not in url or "{y}" not in url:
            raise ValueError("xyzUrl must contain {z}, {x}, and {y} placeholders for tile coordinates")

        return url
