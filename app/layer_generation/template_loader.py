"""
Shared, cached template loading for layer file generation.
"""

import logging
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
