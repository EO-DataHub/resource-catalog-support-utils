"""
Request models for LYRX generation.

Reuses the STAC item and base item/xyzUrl request models shared with QLR
generation; see app.layer_generation.models.
"""

from ..layer_generation.models import STACItem, XYZLayerRequest

__all__ = ["LYRXRequest", "STACItem"]


class LYRXRequest(XYZLayerRequest):
    """
    Request payload for LYRX file generation.

    Contains a STAC item and XYZ tile service URL needed to generate a
    LYRX file for ArcGIS Pro.
    """
