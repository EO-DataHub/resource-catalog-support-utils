from app.layer_generation.filename import safe_filename_component


def test_safe_filename_component_strips_header_injection_chars():
    value = 'x"\r\nX-Injected-Header: evil'
    result = safe_filename_component(value)
    assert "\r" not in result
    assert "\n" not in result
    assert '"' not in result
    assert result == "xX-Injected-Header: evil"


def test_safe_filename_component_strips_backslash():
    assert safe_filename_component(r"back\slash") == "backslash"


def test_safe_filename_component_strips_non_latin1_chars():
    assert safe_filename_component("item-日本語😀-id") == "item--id"


def test_safe_filename_component_all_unsafe_input_returns_empty():
    assert safe_filename_component("😀😀") == ""


def test_safe_filename_component_leaves_normal_ascii_untouched():
    assert safe_filename_component("normal-item-id_123") == "normal-item-id_123"
