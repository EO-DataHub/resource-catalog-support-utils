"""
Template caching module for QLR generation.

This module provides a singleton template cache that loads templates once at startup
and serves them from memory for improved performance.
"""

import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TemplateCache:
    """
    Singleton template cache for storing loaded QLR templates.

    This class ensures templates are loaded only once at startup and cached
    in memory for fast access during request processing.
    """

    _instance: Optional["TemplateCache"] = None
    _templates: Dict[str, str] = {}
    _initialized: bool = False

    def __new__(cls) -> "TemplateCache":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the template cache."""
        if not self._initialized:
            self._templates = {}
            self._initialized = True

    def load_template(self, template_name: str, template_path: str) -> None:
        """
        Load a template from disk and cache it in memory.

        Args:
            template_name: Name to use as cache key
            template_path: Path to the template file

        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file cannot be read
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            self._templates[template_name] = template_content
            logger.info(f"Successfully loaded and cached template: {template_name}")

        except IOError as e:
            logger.error(f"Failed to read template file {template_path}: {e}")
            raise IOError(f"Failed to read template file {template_path}: {e}")

    def get_template(self, template_name: str) -> str:
        """
        Retrieve a cached template by name.

        Args:
            template_name: Name of the template to retrieve

        Returns:
            Template content as string

        Raises:
            KeyError: If template is not found in cache
        """
        if template_name not in self._templates:
            raise KeyError(f"Template '{template_name}' not found in cache")

        return self._templates[template_name]

    def is_loaded(self, template_name: str) -> bool:
        """
        Check if a template is loaded in the cache.

        Args:
            template_name: Name of the template to check

        Returns:
            True if template is cached, False otherwise
        """
        return template_name in self._templates

    def get_loaded_templates(self) -> list[str]:
        """
        Get list of all loaded template names.

        Returns:
            List of template names currently in cache
        """
        return list(self._templates.keys())

    def clear_cache(self) -> None:
        """Clear all cached templates."""
        self._templates.clear()
        logger.info("Template cache cleared")


# Global template cache instance
template_cache = TemplateCache()


def load_templates_at_startup() -> None:
    """
    Load all required templates at application startup.

    This function should be called during FastAPI startup to pre-load
    all templates into memory.
    """
    try:
        # Get the templates directory
        templates_dir = Path(__file__).parent / "templates"

        # Load the generic template
        generic_template_path = templates_dir / "generic_template.xml"
        template_cache.load_template("generic", str(generic_template_path))

        logger.info("All templates loaded successfully at startup")

    except Exception as e:
        logger.error(f"Failed to load templates at startup: {e}")
        raise


def get_cached_template(template_name: str = "generic") -> str:
    """
    Get a cached template by name.

    Args:
        template_name: Name of the template to retrieve (default: "generic")

    Returns:
        Template content as string

    Raises:
        KeyError: If template is not found in cache
    """
    return template_cache.get_template(template_name)
