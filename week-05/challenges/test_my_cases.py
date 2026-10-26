def test_my_summarize_case(summarize_values):
    values = [5, -2, 5, 0, -2, 7, 5]
    before = values.copy()
    expected = {
        "unique": [5, -2, 0, 7],
        "counts": {5: 3, -2: 2, 0: 1, 7: 1},
        "repeated": {5, -2},
    }

    result = summarize_values(values)

    assert result == expected
    assert values == before


def test_my_summarize_empty_case(summarize_values):
    values = []
    before = values.copy()

    result = summarize_values(values)

    assert result == {"unique": [], "counts": {}, "repeated": set()}
    assert values == before
