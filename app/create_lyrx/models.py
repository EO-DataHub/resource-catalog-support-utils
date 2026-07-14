"""
Request models for LYRX generation.

Reuses the STAC item models defined for QLR generation, since the request
shape (STAC item + XYZ tile URL) is identical across both formats.
"""

from pydantic import BaseModel, Field, field_validator

from ..create_qlr.models import STACItem

__all__ = ["LYRXRequest", "STACItem"]


class LYRXRequest(BaseModel):
    """
    Request payload for LYRX file generation.

    Contains a STAC item and XYZ tile service URL needed to generate a
    LYRX file for ArcGIS Pro.
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
