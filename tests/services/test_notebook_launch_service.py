from types import SimpleNamespace

import nbformat
import pytest

from app.core.config import settings
from app.services.notebook_launch_service import (
    NotebookLaunchResult,
    NotebookLaunchService,
    NotebookUploadError,
    TemplateFetchError,
)


class _FakeS3Client:
    def __init__(self) -> None:
        self.put_calls: list[dict] = []

    def put_object(self, **kwargs):
        self.put_calls.append(kwargs)


def _make_template_notebook_json() -> str:
    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            "Collection: {{STAC_COLLECTION_NAME}}, Item: {{STAC_ITEM_LINK}}"
        )
    )
    return nbformat.writes(nb)


def _make_template_with_variables_json() -> str:
    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            "A: {{A}}, B: {{B}}, Missing: {{MISSING}}"
        )
    )
    return nbformat.writes(nb)


def test_launch_notebook_happy_path(monkeypatch):
    template_json = _make_template_notebook_json()

    def fake_get(url, timeout=10):  # noqa: ARG001
        return SimpleNamespace(status_code=200, text=template_json)

    fake_s3 = _FakeS3Client()

    service = NotebookLaunchService(s3_client=fake_s3, http_get=fake_get)

    result: NotebookLaunchResult = service.launch_notebook(
        workspace_name="sparkgeotest",
        username="geodowd",
        action_name="ndvi",
        template_url="https://example.com/templates/ndvi.ipynb",
        variables={
            "STAC_COLLECTION_NAME": "sentinel-s2-l2a",
            "STAC_ITEM_LINK": "https://example.com/stac/item",
        },
    )

    assert result.servername.startswith("ndvi_")
    assert result.notebook_path.startswith("jupyter/")
    assert result.notebook_path.endswith(".ipynb")
    assert "sparkgeotest" in result.spawn_url
    assert "ndvi_" in result.spawn_url

    assert len(fake_s3.put_calls) == 1
    call = fake_s3.put_calls[0]
    assert call["Bucket"] == settings.notebook_s3_bucket
    assert call["Key"].startswith("sparkgeotest/jupyter/")


def test_launch_notebook_template_fetch_error(monkeypatch):
    def fake_get(url, timeout=10):  # noqa: ARG001
        raise RuntimeError("network error")

    fake_s3 = _FakeS3Client()
    service = NotebookLaunchService(s3_client=fake_s3, http_get=fake_get)

    with pytest.raises(TemplateFetchError):
        service.launch_notebook(
            workspace_name="sparkgeotest",
            username="geodowd",
            action_name="ndvi",
            template_url="https://example.com/templates/ndvi.ipynb",
        )

    assert fake_s3.put_calls == []


def test_launch_notebook_upload_error(monkeypatch):
    template_json = _make_template_notebook_json()

    def fake_get(url, timeout=10):  # noqa: ARG001
        return SimpleNamespace(status_code=200, text=template_json)

    class _FailingS3Client:
        def put_object(self, **kwargs):
            raise RuntimeError("s3 error")

    service = NotebookLaunchService(s3_client=_FailingS3Client(), http_get=fake_get)

    with pytest.raises(NotebookUploadError):
        service.launch_notebook(
            workspace_name="sparkgeotest",
            username="geodowd",
            action_name="ndvi",
            template_url="https://example.com/templates/ndvi.ipynb",
        )


def test_launch_notebook_unique_servernames(monkeypatch):
    template_json = _make_template_notebook_json()

    def fake_get(url, timeout=10):  # noqa: ARG001
        return SimpleNamespace(status_code=200, text=template_json)

    fake_s3 = _FakeS3Client()
    service = NotebookLaunchService(s3_client=fake_s3, http_get=fake_get)

    result1 = service.launch_notebook(
        workspace_name="sparkgeotest",
        username="geodowd",
        action_name="ndvi",
        template_url="https://example.com/templates/ndvi.ipynb",
        variables={"STAC_ITEM_LINK": "https://example.com/stac/item1"},
    )

    result2 = service.launch_notebook(
        workspace_name="sparkgeotest",
        username="geodowd",
        action_name="ndvi",
        template_url="https://example.com/templates/ndvi.ipynb",
        variables={"STAC_ITEM_LINK": "https://example.com/stac/item2"},
    )

    assert result1.servername != result2.servername
    assert result1.notebook_path != result2.notebook_path
    assert result1.servername.startswith("ndvi_")
    assert result2.servername.startswith("ndvi_")
    assert len(result1.servername.split("_")) == 2
    assert len(result2.servername.split("_")) == 2


def test_launch_notebook_with_variables(monkeypatch):
    """Test that variables are correctly replaced in notebook template."""
    template_json = _make_template_with_variables_json()

    def fake_get(url, timeout=10):  # noqa: ARG001
        return SimpleNamespace(status_code=200, text=template_json)

    fake_s3 = _FakeS3Client()
    service = NotebookLaunchService(s3_client=fake_s3, http_get=fake_get)

    result = service.launch_notebook(
        workspace_name="sparkgeotest",
        username="geodowd",
        action_name="ndvi",
        template_url="https://example.com/templates/ndvi.ipynb",
        variables={
            "A": "one",
            "B": "two",
        },
    )

    assert len(fake_s3.put_calls) == 1
    uploaded_body = fake_s3.put_calls[0]["Body"]
    uploaded_notebook = nbformat.reads(uploaded_body.decode("utf-8"), as_version=4)
    cell_source = uploaded_notebook.cells[0].source
    assert "{{A}}" not in cell_source
    assert "{{B}}" not in cell_source
    assert "one" in cell_source
    assert "two" in cell_source
    assert "{{MISSING}}" in cell_source  # No value provided, placeholder unchanged


def test_launch_notebook_without_variables(monkeypatch):
    """Test that notebook works when variables is omitted or empty."""
    template_json = _make_template_with_variables_json()

    def fake_get(url, timeout=10):  # noqa: ARG001
        return SimpleNamespace(status_code=200, text=template_json)

    fake_s3 = _FakeS3Client()
    service = NotebookLaunchService(s3_client=fake_s3, http_get=fake_get)

    result = service.launch_notebook(
        workspace_name="sparkgeotest",
        username="geodowd",
        action_name="ndvi",
        template_url="https://example.com/templates/ndvi.ipynb",
    )

    assert len(fake_s3.put_calls) == 1
    uploaded_body = fake_s3.put_calls[0]["Body"]
    uploaded_notebook = nbformat.reads(uploaded_body.decode("utf-8"), as_version=4)
    cell_source = uploaded_notebook.cells[0].source
    assert "{{A}}" in cell_source
    assert "{{B}}" in cell_source
    assert "{{MISSING}}" in cell_source

