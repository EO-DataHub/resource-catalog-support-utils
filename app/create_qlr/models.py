"""
Request models for QLR generation.

Reuses the STAC item and base item/xyzUrl request models shared with LYRX
generation; see app.layer_generation.models.
"""

from ..layer_generation.models import STACItem, XYZLayerRequest

__all__ = ["QLRRequest", "STACItem"]


class QLRRequest(XYZLayerRequest):
    """
    Request payload for QLR file generation.

    Contains a STAC item and XYZ tile service URL needed to generate a
    QLR file for QGIS.
    """
