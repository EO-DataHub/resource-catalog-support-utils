"""
API endpoints for launching parameterized Jupyter notebooks.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import AnyHttpUrl, BaseModel

from app.services.notebook_launch_service import (
    NotebookLaunchResult,
    NotebookLaunchService,
    NotebookUploadError,
    TemplateFetchError,
    TemplateParseError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class NotebookLaunchRequest(BaseModel):
    """Request body for launching a notebook."""

    workspace_name: str
    username: str
    action_name: str
    template_url: AnyHttpUrl
    variables: dict[str, str] | None = None  # Optional template variables: key -> {{KEY}} placeholder value


class NotebookLaunchSuccess(BaseModel):
    """Successful launch response."""

    servername: str
    notebook_path: str
    spawn_url: str


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: str
    code: str


def get_notebook_launch_service() -> NotebookLaunchService:
    """FastAPI dependency provider for the launch service."""
    return NotebookLaunchService()


ServiceDep = Annotated[NotebookLaunchService, Depends(get_notebook_launch_service)]


@router.post(
    "/notebooks/launch",
    response_model=NotebookLaunchSuccess,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def launch_notebook(
    payload: NotebookLaunchRequest,
    service: ServiceDep,
) -> JSONResponse | NotebookLaunchSuccess:
    """
    Launch a parameterized notebook from a template and return spawn details.
    """
    try:
        result: NotebookLaunchResult = service.launch_notebook(
            workspace_name=payload.workspace_name,
            username=payload.username,
            action_name=payload.action_name,
            template_url=str(payload.template_url),
            variables=payload.variables,
        )
        return NotebookLaunchSuccess(
            servername=result.servername,
            notebook_path=result.notebook_path,
            spawn_url=result.spawn_url,
        )
    except TemplateFetchError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(exc), "code": TemplateFetchError.code},
        )
    except TemplateParseError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(exc), "code": TemplateParseError.code},
        )
    except NotebookUploadError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(exc), "code": NotebookUploadError.code},
        )
    except Exception:
        logger.exception("Unexpected error during notebook launch")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error", "code": "INTERNAL_ERROR"},
        )
