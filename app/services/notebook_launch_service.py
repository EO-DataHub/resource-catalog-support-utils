"""
Service for launching parameterized Jupyter notebooks.

This module is responsible for:
- Fetching notebook templates from a URL
- Injecting template variables (placeholder substitution)
- Uploading the parameterized notebook to S3
- Constructing the JupyterHub spawn URL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import boto3
import nbformat
import requests
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class TemplateFetchError(Exception):
    """Raised when the template notebook cannot be fetched."""

    code = "TEMPLATE_FETCH_FAILED"


class TemplateParseError(Exception):
    """Raised when the template notebook cannot be parsed."""

    code = "TEMPLATE_PARSE_FAILED"


class NotebookUploadError(Exception):
    """Raised when the parameterized notebook cannot be uploaded to S3."""

    code = "NOTEBOOK_UPLOAD_FAILED"


@dataclass
class NotebookLaunchResult:
    """Result of a successful notebook launch preparation."""

    servername: str
    notebook_path: str
    spawn_url: str


class NotebookLaunchService:
    """
    Core service for notebook launch operations.

    This class is written to be easy to unit test by allowing injection of the
    S3 client and HTTP client (requests.get) where needed.
    """

    def __init__(
        self,
        s3_client: Any | None = None,
        http_get: Any | None = None,
    ) -> None:
        self._settings = settings
        self._s3_client = s3_client or boto3.client("s3")
        self._http_get = http_get or requests.get

    # ---- Public API -----------------------------------------------------

    def launch_notebook(
        self,
        *,
        workspace_name: str,
        username: str,
        action_name: str,
        template_url: str,
        variables: dict[str, str] | None = None,
    ) -> NotebookLaunchResult:
        """
        Fetch, parameterize, upload, and prepare a notebook for launch.
        """
        servername = self._generate_servername(action_name)
        logger.info(
            "Launching notebook",
            extra={
                "username": username,
                "workspace": workspace_name,
                "action_name": action_name,
                "servername": servername,
            },
        )

        template_nb = self._fetch_and_parse_template(template_url)

        parameterized_nb = self._parameterize_notebook(
            template_nb=template_nb,
            variables=variables,
        )

        notebook_path = self._build_notebook_path(servername)
        s3_key = self._build_s3_key(workspace_name, servername)

        self._upload_notebook_to_s3(parameterized_nb, s3_key)

        spawn_url = self._build_spawn_url(
            username=username,
            workspace_name=workspace_name,
            servername=servername,
            notebook_path=notebook_path,
        )

        logger.info(
            "Notebook launch prepared",
            extra={
                "username": username,
                "workspace": workspace_name,
                "action_name": action_name,
                "servername": servername,
                "notebook_path": notebook_path,
            },
        )

        return NotebookLaunchResult(
            servername=servername,
            notebook_path=notebook_path,
            spawn_url=spawn_url,
        )

    # ---- Internal helpers -----------------------------------------------

    def _generate_servername(self, action_name: str) -> str:
        """Generate a unique server name using the action name and a UUID4."""
        return f"{action_name}_{uuid4().hex}"

    def _fetch_and_parse_template(self, template_url: str) -> nbformat.NotebookNode:
        """Fetch the template from the given URL and parse as a notebook."""
        try:
            response = self._http_get(template_url, timeout=10)
        except (requests.RequestException, Exception) as exc:  # type: ignore[reportUnknownArgumentType]
            logger.error(
                "Failed to fetch notebook template",
                extra={"template_url": template_url},
            )
            raise TemplateFetchError(str(exc)) from exc

        if response.status_code != 200:
            logger.error(
                "Template URL returned non-200 status",
                extra={
                    "template_url": template_url,
                    "status_code": response.status_code,
                },
            )
            raise TemplateFetchError(
                f"Template URL returned status {response.status_code}"
            )

        try:
            return nbformat.reads(response.text, as_version=4)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to parse notebook template JSON",
                extra={"template_url": template_url},
            )
            raise TemplateParseError("Template is not valid notebook JSON") from exc

    def _parameterize_notebook(
        self,
        *,
        template_nb: nbformat.NotebookNode,
        variables: dict[str, str] | None = None,
    ) -> nbformat.NotebookNode:
        """
        Replace placeholders in the notebook source with values from variables.

        Each key K in variables is replaced as {{K}} -> value in all cell sources.
        Uses simple string substitution.
        """
        replacements = {}
        if variables:
            for key, value in variables.items():
                replacements[f"{{{{{key}}}}}"] = value

        for cell in template_nb.cells:
            source = getattr(cell, "source", None)
            if not isinstance(source, str):
                continue
            for placeholder, value in replacements.items():
                if placeholder in source:
                    source = source.replace(placeholder, value)
            cell.source = source

        return template_nb

    def _build_notebook_path(self, servername: str) -> str:
        """
        Build the relative notebook path used in the response and Jupyter UI.
        """
        return f"jupyter/{servername}.ipynb"

    def _build_s3_key(self, workspace_name: str, servername: str) -> str:
        """
        Build the S3 key within the notebooks bucket.

        Matches: <workspace_name>/jupyter/<servername>.ipynb
        """
        return f"{workspace_name}/jupyter/{servername}.ipynb"

    def _upload_notebook_to_s3(
        self,
        notebook: nbformat.NotebookNode,
        s3_key: str,
    ) -> None:
        """Upload the parameterized notebook to the configured S3 bucket."""
        bucket = self._settings.notebook_s3_bucket
        body = nbformat.writes(notebook).encode("utf-8")

        try:
            self._s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=body,
                ContentType="application/x-ipynb+json",
            )
        except (BotoCoreError, ClientError, Exception) as exc:
            logger.error(
                "Failed to upload notebook to S3",
                extra={
                    "bucket": bucket,
                    "key": s3_key,
                },
            )
            raise NotebookUploadError(str(exc)) from exc

    def _build_spawn_url(
        self,
        *,
        username: str,
        workspace_name: str,
        servername: str,
        notebook_path: str,
    ) -> str:
        """
        Construct the JupyterHub spawn URL according to the documented format.
        """
        base = self._settings.jupyterhub_base_url.rstrip("/")
        next_url = (
            f"{base}/user/{username}/{servername}/lab/tree/s3/{notebook_path}"
        )
        return (
            f"{base}/hub/spawn/{username}/{servername}"
            f"?workspace={workspace_name}&next={next_url}"
        )

