"""CORS preflight behaviour for the frontends that call this service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PREFLIGHT_HEADERS = {
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization,content-type",
}


@pytest.mark.parametrize(
    "origin",
    [
        "https://eodatahub.org.uk",
        "https://eodhrc.eodatahub.org.uk",
        "https://preview.eodatahub.org.uk",
    ],
)
def test_preflight_allows_frontend_origins(origin: str) -> None:
    response = client.options(
        "/api/v1/notebooks/launch",
        headers={"Origin": origin, **PREFLIGHT_HEADERS},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_preflight_rejects_unknown_origin() -> None:
    response = client.options(
        "/api/v1/notebooks/launch",
        headers={"Origin": "https://example.org", **PREFLIGHT_HEADERS},
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
