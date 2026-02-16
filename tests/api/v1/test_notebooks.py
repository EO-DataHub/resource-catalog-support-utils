import types

from fastapi.testclient import TestClient

from app.main import app
from app.api.v1 import notebooks
from app.services.notebook_launch_service import (
    NotebookLaunchResult,
    TemplateFetchError,
)


client = TestClient(app)


class _FakeLaunchServiceSuccess:
    def launch_notebook(self, **kwargs):
        return NotebookLaunchResult(
            servername="ndvi_123456",
            notebook_path="jupyter/ndvi_123456.ipynb",
            spawn_url=(
                "https://eodatahub-workspaces.org.uk/notebooks/hub/spawn/"
                "geodowd/ndvi_123456?workspace=sparkgeotest&next="
                "https://eodatahub-workspaces.org.uk/notebooks/user/"
                "geodowd/ndvi_123456/lab/tree/s3/jupyter/ndvi_123456.ipynb"
            ),
        )


class _FakeLaunchServiceTemplateError:
    def launch_notebook(self, **kwargs):
        raise TemplateFetchError("Template notebook could not be fetched")


def _override_service_success():
    return _FakeLaunchServiceSuccess()


def _override_service_template_error():
    return _FakeLaunchServiceTemplateError()


def test_launch_notebook_happy_path():
    app.dependency_overrides[notebooks.get_notebook_launch_service] = (
        _override_service_success
    )

    payload = {
        "workspace_name": "sparkgeotest",
        "username": "geodowd",
        "action_name": "ndvi",
        "template_url": "https://example.com/templates/ndvi.ipynb",
    }

    response = client.post("/api/v1/notebooks/launch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["servername"] == "ndvi_123456"
    assert data["notebook_path"] == "jupyter/ndvi_123456.ipynb"
    assert data["spawn_url"].startswith(
        "https://eodatahub-workspaces.org.uk/notebooks/hub/spawn/"
    )

    app.dependency_overrides.pop(notebooks.get_notebook_launch_service, None)


def test_launch_notebook_template_error():
    app.dependency_overrides[notebooks.get_notebook_launch_service] = (
        _override_service_template_error
    )

    payload = {
        "workspace_name": "sparkgeotest",
        "username": "geodowd",
        "action_name": "ndvi",
        "template_url": "https://example.com/templates/ndvi.ipynb",
    }

    response = client.post("/api/v1/notebooks/launch", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == TemplateFetchError.code
    assert "Template notebook could not be fetched" in data["error"]

    app.dependency_overrides.pop(notebooks.get_notebook_launch_service, None)


# Create a singleton instance that persists across calls
_unique_servernames_service_instance = None


class _FakeLaunchServiceUniqueServernames:
    def __init__(self):
        self._call_count = 0

    def launch_notebook(self, **kwargs):
        self._call_count += 1
        unique_id = f"unique{self._call_count}"
        return NotebookLaunchResult(
            servername=f"ndvi_{unique_id}",
            notebook_path=f"jupyter/ndvi_{unique_id}.ipynb",
            spawn_url=(
                f"https://eodatahub-workspaces.org.uk/notebooks/hub/spawn/"
                f"geodowd/ndvi_{unique_id}?workspace=sparkgeotest&next="
                f"https://eodatahub-workspaces.org.uk/notebooks/user/"
                f"geodowd/ndvi_{unique_id}/lab/tree/s3/jupyter/ndvi_{unique_id}.ipynb"
            ),
        )


def _override_service_unique_servernames():
    global _unique_servernames_service_instance
    if _unique_servernames_service_instance is None:
        _unique_servernames_service_instance = _FakeLaunchServiceUniqueServernames()
    return _unique_servernames_service_instance


def test_launch_notebook_distinct_servernames():
    app.dependency_overrides[notebooks.get_notebook_launch_service] = (
        _override_service_unique_servernames
    )

    payload = {
        "workspace_name": "sparkgeotest",
        "username": "geodowd",
        "action_name": "ndvi",
        "template_url": "https://example.com/templates/ndvi.ipynb",
    }

    response1 = client.post("/api/v1/notebooks/launch", json=payload)
    assert response1.status_code == 200
    data1 = response1.json()

    response2 = client.post("/api/v1/notebooks/launch", json=payload)
    assert response2.status_code == 200
    data2 = response2.json()

    assert data1["servername"] != data2["servername"]
    assert data1["notebook_path"] != data2["notebook_path"]
    assert data1["servername"].startswith("ndvi_")
    assert data2["servername"].startswith("ndvi_")

    app.dependency_overrides.pop(notebooks.get_notebook_launch_service, None)
    # Reset the singleton for next test run
    global _unique_servernames_service_instance
    _unique_servernames_service_instance = None


def test_launch_notebook_with_variables():
    """Test that variables can be passed in the API request."""
    app.dependency_overrides[notebooks.get_notebook_launch_service] = (
        _override_service_success
    )

    payload = {
        "workspace_name": "sparkgeotest",
        "username": "geodowd",
        "action_name": "ndvi",
        "template_url": "https://example.com/templates/ndvi.ipynb",
        "variables": {
            "STAC_COLLECTION_NAME": "sentinel-s2-l2a",
            "STAC_ITEM_LINK": "https://example.com/stac/item",
        },
    }

    response = client.post("/api/v1/notebooks/launch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["servername"] == "ndvi_123456"
    assert data["notebook_path"] == "jupyter/ndvi_123456.ipynb"

    app.dependency_overrides.pop(notebooks.get_notebook_launch_service, None)


def test_launch_notebook_without_variables():
    """Test that API works correctly when variables is not provided."""
    app.dependency_overrides[notebooks.get_notebook_launch_service] = (
        _override_service_success
    )

    payload = {
        "workspace_name": "sparkgeotest",
        "username": "geodowd",
        "action_name": "ndvi",
        "template_url": "https://example.com/templates/ndvi.ipynb",
    }

    response = client.post("/api/v1/notebooks/launch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["servername"] == "ndvi_123456"
    assert data["notebook_path"] == "jupyter/ndvi_123456.ipynb"

    app.dependency_overrides.pop(notebooks.get_notebook_launch_service, None)

