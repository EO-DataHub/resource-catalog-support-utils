"""
Shared, cached template loading for layer file generation.
"""

import logging
from collections.abc import Callable
from functools import cache
from pathlib import Path

logger = logging.getLogger(__name__)


class TemplateUnavailableError(Exception):
    """Raised when a layer generation template file cannot be loaded from disk."""


@cache
def load_template(template_path: Path) -> str:
    """
    Load a template from disk, caching its contents in memory.

    Template files are static content, so the disk read only happens once
    per process per path; subsequent calls are served from cache.

    Args:
        template_path: Absolute path to the template file

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template file doesn't exist
        IOError: If template file cannot be read
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    try:
        with open(template_path, encoding="utf-8") as f:
            template_content = f.read()

        logger.debug(f"Successfully loaded template: {template_path.name}")
        return template_content

    except OSError as e:
        logger.error(f"Failed to read template file {template_path}: {e}")
        raise OSError(f"Failed to read template file {template_path}: {e}") from e


def generate_from_template(template_path: Path, format_name: str, render: Callable[[str], str]) -> str:
    """
    Load a template and render it, applying the shared format-agnostic error handling.

    Args:
        template_path: Absolute path to the template file
        format_name: Human-readable format name for error messages (e.g. "QLR", "LYRX")
        render: Callable that takes the loaded template content and returns the
            generated document

    Returns:
        The generated document content as a string

    Raises:
        TemplateUnavailableError: If the template file cannot be loaded
        ValueError: If rendering the template fails
    """
    try:
        template = load_template(template_path)
    except (OSError, FileNotFoundError) as e:
        logger.error(f"Failed to load template: {e}")
        raise TemplateUnavailableError(f"{format_name} template is unavailable") from e

    try:
        return render(template)
    except Exception as e:
        error_msg = f"Failed to generate {format_name} from template"
        logger.error(f"{error_msg}: {e}")
        raise ValueError(f"{error_msg}: {e!s}") from e
