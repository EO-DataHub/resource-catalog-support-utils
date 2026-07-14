from app.create_qlr.create_qlr import generate_qlr_from_xyz


def test_generate_qlr_from_xyz_empty_layer_id_falls_back_to_default():
    qlr_xml = generate_qlr_from_xyz(
        xyz_url="https://example.com/{z}/{x}/{y}",
        layer_id="",
        layer_name="Some Layer",
    )

    assert "<id>unknown_layer</id>" in qlr_xml
    assert 'id="unknown_layer"' in qlr_xml


def test_generate_qlr_from_xyz_empty_layer_name_falls_back_to_default():
    qlr_xml = generate_qlr_from_xyz(
        xyz_url="https://example.com/{z}/{x}/{y}",
        layer_id="some-id",
        layer_name="",
    )

    assert "<layername>unknown_layer</layername>" in qlr_xml
    assert 'name="unknown_layer"' in qlr_xml


def test_generate_qlr_from_xyz_encodes_tile_placeholders_and_ampersand():
    qlr_xml = generate_qlr_from_xyz(
        xyz_url="https://example.com/tiles/{z}/{x}/{y}?a=1&b=2",
        layer_id="my-id",
        layer_name="My Layer",
    )

    assert "%7Bz%7D/%7Bx%7D/%7By%7D" in qlr_xml
    assert "a=1%26b=2" in qlr_xml
