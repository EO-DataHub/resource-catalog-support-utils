from pathlib import Path

import pytest

from app.layer_generation.template_loader import TemplateUnavailableError, generate_from_template


def test_generate_from_template_returns_rendered_content(tmp_path):
    template_path = tmp_path / "template.txt"
    template_path.write_text("hello")

    result = generate_from_template(template_path, "TEST", lambda template: template.upper())

    assert result == "HELLO"


def test_generate_from_template_missing_file_raises_template_unavailable_error():
    missing_path = Path("/nonexistent/does-not-exist.txt")

    with pytest.raises(TemplateUnavailableError, match="TEST template is unavailable"):
        generate_from_template(missing_path, "TEST", lambda template: template)


def test_generate_from_template_render_error_wrapped_as_value_error(tmp_path):
    template_path = tmp_path / "template.txt"
    template_path.write_text("hello")

    def failing_render(template: str) -> str:
        raise KeyError("missing_placeholder")

    with pytest.raises(ValueError, match="Failed to generate TEST from template"):
        generate_from_template(template_path, "TEST", failing_render)
