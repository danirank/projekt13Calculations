import app.services.calculation_service as calculation_service
from app.models.data_classes import (
    FilterValue,
    GroupReduction,
    KvotReduce,
    MarketOddsReduce,
    PeopleOddsReduce,
    ReductionFilterDto,
    SignPick,
)

mock_row = ["1X", "1X", "1X", "1", "1", "2", "X", "X", "1", "1", "1", "1", "1"]
mock_filter_value = FilterValue(
    Market=MarketOddsReduce(MinOdds=0.0, MaxOdds=100000000),
    People=PeopleOddsReduce(MinOdds=None, MaxOdds=None),
    Kvot=KvotReduce(MinKvot=None, MaxKvot=None),
)
mock_sign_filter = ReductionFilterDto(
    groups=[
        GroupReduction(
            picks=[
                SignPick(match_no=1, sign="1"),
                SignPick(match_no=2, sign="1"),
                SignPick(match_no=3, sign="1"),
            ],
            min_hits=1,
            max_hits=2,
        )
    ]
)


def test_reduce_service_adds_values_then_filters(monkeypatch):
    captured = {}

    def fake_append_calculations_to_all_rows(base_row, coupon):
        captured["base_row"] = base_row
        captured["coupon"] = coupon
        return ["expanded"]

    def fake_filter_value_and_row_reductions(rows, filter_value, reduce_filter):
        captured["rows"] = rows
        captured["filter_value"] = filter_value
        captured["reduce_filter"] = reduce_filter
        return ["filtered"]

    monkeypatch.setattr(
        calculation_service,
        "append_calculations_to_all_rows",
        fake_append_calculations_to_all_rows,
    )
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
        "coupon": ["coupon"],
        "rows": ["expanded"],
        "filter_value": "filters",
        "reduce_filter": "reductions",
    }


def test_reduce_service_returns_filter_result_without_using_coupon(monkeypatch):
    def fake_append_calculations_to_all_rows(base_row, coupon):
        return {"base_row": base_row, "coupon": coupon}

    def fake_filter_value_and_row_reductions(rows, filter_value, reduce_filter):
        return {
            "rows": rows,
            "filter_value": filter_value,
            "reduce_filter": reduce_filter,
        }

    monkeypatch.setattr(
        calculation_service,
        "append_calculations_to_all_rows",
        fake_append_calculations_to_all_rows,
    )
    monkeypatch.setattr(
        calculation_service,
        "filter_value_and_row_reductions",
        fake_filter_value_and_row_reductions,
    )

    result = calculation_service.reduce_service(["1", "X"], ["ignored"], None, "reduce")

    assert result == {
        "rows": {"base_row": ["1", "X"], "coupon": ["ignored"]},
        "filter_value": None,
        "reduce_filter": "reduce",
    }


def test_reduce_service_with_13_games_passes_rows_to_filter(monkeypatch):
    captured = {}

    def fake_append_calculations_to_all_rows(base_row, coupon):
        captured["base_row"] = base_row
        captured["coupon"] = coupon
        return ["row1", "row2", "row3", "row4"]

    def fake_filter_value_and_row_reductions(rows, filter_value, reduce_filter):
        captured["rows"] = rows
        captured["filter_value"] = filter_value
        captured["reduce_filter"] = reduce_filter
        return rows[:3]

    monkeypatch.setattr(
        calculation_service,
        "append_calculations_to_all_rows",
        fake_append_calculations_to_all_rows,
    )

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

    assert captured["base_row"] == mock_row
    assert captured["coupon"] == []
    assert captured["rows"] == ["row1", "row2", "row3", "row4"]
    assert captured["filter_value"] == mock_filter_value
    assert captured["reduce_filter"] == mock_sign_filter
    assert result == captured["rows"][:3]
