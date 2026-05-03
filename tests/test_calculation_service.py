import app.services.calculation_service as calculation_service
from app.data.mock_coupon import mock_filter_value, mock_row, mock_sign_filter


def test_reduce_service_uses_generated_single_rows(monkeypatch):
    captured = {}

    def fake_get_single_rows(base_row):
        captured["base_row"] = base_row
        return ["expanded"]

    def fake_filter_value_and_row_reductions(single_rows, filter_value, reduce_filter):
        captured["single_rows"] = single_rows
        captured["filter_value"] = filter_value
        captured["reduce_filter"] = reduce_filter
        return ["filtered"]

    monkeypatch.setattr(calculation_service, "getSingleRows", fake_get_single_rows)
    monkeypatch.setattr(
        calculation_service,
        "filter_value_and_row_reductions",
        fake_filter_value_and_row_reductions,
    )

    result = calculation_service.reduce_service(
        ["1X"], ["coupon"], "filters", "reductions"
    )

    assert result == ["filtered"]
    assert captured == {
        "base_row": ["1X"],
        "single_rows": ["expanded"],
        "filter_value": "filters",
        "reduce_filter": "reductions",
    }


def test_reduce_service_returns_filter_result_without_using_coupon(monkeypatch):
    def fake_get_single_rows(base_row):
        return [tuple(base_row)]

    def fake_filter_value_and_row_reductions(single_rows, filter_value, reduce_filter):
        return {
            "rows": single_rows,
            "filter_value": filter_value,
            "reduce_filter": reduce_filter,
        }

    monkeypatch.setattr(calculation_service, "getSingleRows", fake_get_single_rows)
    monkeypatch.setattr(
        calculation_service,
        "filter_value_and_row_reductions",
        fake_filter_value_and_row_reductions,
    )

    result = calculation_service.reduce_service(["1", "X"], ["ignored"], None, "reduce")

    assert result == {
        "rows": [("1", "X")],
        "filter_value": None,
        "reduce_filter": "reduce",
    }


def test_reduce_service_with_13_games_returns_reduced_rows(monkeypatch):
    captured = {}

    def fake_filter_value_and_row_reductions(single_rows, filter_value, reduce_filter):
        captured["single_rows"] = single_rows
        captured["filter_value"] = filter_value
        captured["reduce_filter"] = reduce_filter
        return single_rows[:3]

    monkeypatch.setattr(
        calculation_service,
        "filter_value_and_row_reductions",
        fake_filter_value_and_row_reductions,
    )

    result = calculation_service.reduce_service(
        mock_row,
        [],
        mock_filter_value,
        mock_sign_filter,
    )

    assert len(captured["single_rows"]) == 8
    assert captured["single_rows"][0] == (
        "1",
        "1",
        "1",
        "1",
        "1",
        "2",
        "X",
        "X",
        "1",
        "1",
        "1",
        "1",
        "1",
    )
    assert captured["single_rows"][-1] == (
        "X",
        "X",
        "X",
        "1",
        "1",
        "2",
        "X",
        "X",
        "1",
        "1",
        "1",
        "1",
        "1",
    )
    assert captured["filter_value"] == mock_filter_value
    assert captured["reduce_filter"] == mock_sign_filter
    assert result == captured["single_rows"][:3]
