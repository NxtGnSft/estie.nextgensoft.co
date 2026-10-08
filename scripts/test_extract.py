from extract import parse_dimensions, parse_specs, title_case


def test_parse_dimensions_three_numbers():
    assert parse_dimensions("45 x 52 x 83 cm") == {"raw": "45 x 52 x 83 cm", "w": 45, "d": 52, "h": 83}


def test_parse_dimensions_decimal_comma():
    assert parse_dimensions("55 x 47,5 x 74,5 cm") == {"raw": "55 x 47,5 x 74,5 cm", "w": 55, "d": 47.5, "h": 74.5}


def test_parse_dimensions_with_letters():
    assert parse_dimensions("W 79 x D 88 x H 70 cm") == {"raw": "W 79 x D 88 x H 70 cm", "w": 79, "d": 88, "h": 70}


def test_parse_dimensions_round_table_keeps_raw_only():
    assert parse_dimensions("D115 x 76 cm") == {"raw": "D115 x 76 cm"}


def test_parse_specs_two_span_rows():
    rows = ["HIROSHIMA CHAIR", "Material : Teak wood", "Dimension: 45 x 52 x 83 cm", "Finish : By request"]
    assert parse_specs(rows) == {
        "name": "Hiroshima Chair", "material": "Teak wood",
        "dimensions": {"raw": "45 x 52 x 83 cm", "w": 45, "d": 52, "h": 83},
        "finish": "By request", "fabric": None, "leather": None,
    }


def test_parse_specs_value_continues_on_next_row():
    rows = ["JANET TABLE", "Material:", "Teak wood", "Dimension: 90 x 78 cm", "Finish: By request"]
    out = parse_specs(rows)
    assert out["material"] == "Teak wood"
    assert out["dimensions"] == {"raw": "90 x 78 cm"}


def test_parse_specs_fabric_and_leather():
    rows = ["SELLY DINING CHAIR", "Material : Teak wood", "Dimension: 50 x 55 x 75 cm",
            "Finish : By request", "Leather : By request"]
    out = parse_specs(rows)
    assert out["leather"] == "By request" and out["fabric"] is None


def test_title_case_keeps_ampersand_and_short_words():
    assert title_case("SIDEBOARD & TV CABINET") == "Sideboard & TV Cabinet"
    assert title_case("CEA DINING ARMCHAIR") == "Cea Dining Armchair"
