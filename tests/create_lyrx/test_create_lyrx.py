import json

from app.create_lyrx.create_lyrx import generate_lyrx_from_xyz


def test_generate_lyrx_from_xyz_empty_layer_id_falls_back_to_default():
    lyrx_json = generate_lyrx_from_xyz(
        xyz_url="https://example.com/{z}/{x}/{y}",
        layer_id="",
        layer_name="Some Layer",
    )

    data = json.loads(lyrx_json)
    assert data["layers"] == ["CIMPATH=Map/unknown_layer.json"]


def test_generate_lyrx_from_xyz_empty_layer_name_falls_back_to_default():
    lyrx_json = generate_lyrx_from_xyz(
        xyz_url="https://example.com/{z}/{x}/{y}",
        layer_id="some-id",
        layer_name="",
    )

    data = json.loads(lyrx_json)
    assert data["layerDefinitions"][0]["name"] == "unknown_layer"


def test_generate_lyrx_from_xyz_produces_valid_json_for_quote_and_backslash_in_id():
    lyrx_json = generate_lyrx_from_xyz(
        xyz_url="https://example.com/{z}/{x}/{y}",
        layer_id='weird"id\\value',
        layer_name="My Layer",
    )

    data = json.loads(lyrx_json)
    assert data["layerDefinitions"][0]["uRI"] == 'CIMPATH=Map/weird"id\\value.json'


def test_generate_lyrx_from_xyz_does_not_re_substitute_dollar_sign_in_value():
    # A layer_id containing a literal placeholder-like string must be inserted
    # verbatim, not expanded again by a second substitution pass.
    lyrx_json = generate_lyrx_from_xyz(
        xyz_url="https://example.com/{z}/{x}/{y}",
        layer_id="${LAYER_NAME}",
        layer_name="Actual Name",
    )

    data = json.loads(lyrx_json)
    assert data["layerDefinitions"][0]["uRI"] == "CIMPATH=Map/${LAYER_NAME}.json"
    assert data["layerDefinitions"][0]["name"] == "Actual Name"
