"""Student tests for independent experiment variants."""


def test_returns_expected_content_and_preserves_source(make_variant):
    source = {"seed": 123, "sample_sizes": [30, 50, 1000]}
    expected_source = {"seed": 123, "sample_sizes": [30, 50, 1000]}
    expected_variant = {"seed": 456, "sample_sizes": [30, 200, 1000]}

    variant = make_variant(source, seed=456, index=1, replacement=200)

    assert variant == expected_variant
    assert source == expected_source


def test_returned_dict_and_sample_sizes_are_independent(make_variant):
    source = {"seed": 123, "sample_sizes": [30, 50, 1000]}
    variant = make_variant(source, seed=456, index=1, replacement=200)

    assert variant is not source
    assert variant["sample_sizes"] is not source["sample_sizes"]


def test_modifying_returned_variant_does_not_change_source(make_variant):
    source = {"seed": 123, "sample_sizes": [30, 50, 1000]}
    expected_source = {"seed": 123, "sample_sizes": [30, 50, 1000]}
    variant = make_variant(source, seed=456, index=1, replacement=200)

    variant["seed"] = 789
    variant["sample_sizes"][0] = 999

    assert source == expected_source


def test_repeated_calls_return_independent_variants(make_variant):
    source = {"seed": 123, "sample_sizes": [30, 50, 1000]}
    expected_source = {"seed": 123, "sample_sizes": [30, 50, 1000]}
    expected_variant = {"seed": 456, "sample_sizes": [30, 200, 1000]}
    first = make_variant(source, seed=456, index=1, replacement=200)
    second = make_variant(source, seed=456, index=1, replacement=200)

    assert first == expected_variant
    assert second == expected_variant
    assert first == second
    assert first is not second
    assert first["sample_sizes"] is not second["sample_sizes"]

    first["seed"] = 789
    first["sample_sizes"][0] = 999

    assert second == expected_variant
    assert source == expected_source
