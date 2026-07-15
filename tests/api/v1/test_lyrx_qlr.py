"""
Integration tests for the /api/v1/qlr and /api/v1/lyrx endpoints.

Focused on the Content-Disposition filename handling and layer_id fallback
behavior that must stay identical between the two sibling endpoints.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_VALID_XYZ_URL = "https://example.com/tiles/{z}/{x}/{y}"


def _stac_item(item_id: str) -> dict:
    return {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": item_id,
        "collection": "test-collection",
        "bbox": [0, 0, 1, 1],
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "properties": {"datetime": "2024-01-01T00:00:00Z"},
        "links": [],
        "assets": {},
    }


def test_qlr_and_lyrx_sanitize_header_injection_identically():
    item_id = 'x"\r\nX-Injected-Header: evil'
    body = {"item": _stac_item(item_id), "xyzUrl": _VALID_XYZ_URL}

    qlr_response = client.post("/api/v1/qlr", json=body)
    lyrx_response = client.post("/api/v1/lyrx", json=body)

    assert qlr_response.status_code == 200
    assert lyrx_response.status_code == 200

    qlr_disposition = qlr_response.headers["content-disposition"]
    lyrx_disposition = lyrx_response.headers["content-disposition"]

    assert qlr_disposition == 'attachment; filename="xX-Injected-Header: evil.qlr"'
    assert lyrx_disposition == 'attachment; filename="xX-Injected-Header: evil.lyrx"'


def test_qlr_and_lyrx_fall_back_filename_for_non_latin1_id():
    body = {"item": _stac_item("日本語😀"), "xyzUrl": _VALID_XYZ_URL}

    qlr_response = client.post("/api/v1/qlr", json=body)
    lyrx_response = client.post("/api/v1/lyrx", json=body)

    assert qlr_response.status_code == 200
    assert lyrx_response.status_code == 200
    assert qlr_response.headers["content-disposition"] == 'attachment; filename="unknown_layer.qlr"'
    assert lyrx_response.headers["content-disposition"] == 'attachment; filename="unknown_layer.lyrx"'


def test_qlr_empty_id_uses_default_layer_id_like_lyrx():
    body = {"item": _stac_item(""), "xyzUrl": _VALID_XYZ_URL}

    qlr_response = client.post("/api/v1/qlr", json=body)

    assert qlr_response.status_code == 200
    assert "<id>unknown_layer</id>" in qlr_response.text
    assert 'id="unknown_layer"' in qlr_response.text


def test_lyrx_empty_id_uses_default_layer_id():
    body = {"item": _stac_item(""), "xyzUrl": _VALID_XYZ_URL}

    lyrx_response = client.post("/api/v1/lyrx", json=body)

    assert lyrx_response.status_code == 200
    assert "CIMPATH=Map/unknown_layer.json" in lyrx_response.text
