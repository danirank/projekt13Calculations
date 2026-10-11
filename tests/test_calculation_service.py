import app.services.calculation_service as calculation_service
from app.models.data_classes import (
    FilterValue,
    GroupReduction,
    KvotReduce,
    MarketOddsReduce,
    PeopleOddsReduce,
    ReductionFilterDto,
    Row,
    SignRepresentationDto,
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
mock_filtered_row = Row(signs=["1"], kvot=1.0, people_odds=2.0, market_odds=3.0)
mock_representation = SignRepresentationDto(
    match_no=1,
    sign="1",
    count=1,
    percentage=100.0,
)


def test_reduce_service_adds_values_then_filters(monkeypatch):
    captured = {}
    expanded_rows = [mock_filtered_row]
    filtered_rows = [mock_filtered_row]

    def fake_append_calculations_to_all_rows(base_row, coupon):
        captured["base_row"] = base_row
        captured["coupon"] = coupon
        return expanded_rows

    def fake_filter_value_and_row_reductions(rows, filter_value, reduce_filter):
        captured["rows"] = rows
        captured["filter_value"] = filter_value
        captured["reduce_filter"] = reduce_filter
        return filtered_rows

    def fake_calculate_sign_representations(rows, number_of_matches):
        captured["representation_rows"] = rows
        captured["number_of_matches"] = number_of_matches
        return [mock_representation]

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
    monkeypatch.setattr(
        calculation_service,
        "calculate_sign_representations",
        fake_calculate_sign_representations,
    )

    result = calculation_service.reduce_service(
        ["1X"], [], mock_filter_value, mock_sign_filter
    )

    assert result.rows == filtered_rows
    assert result.sign_representations == [mock_representation]
    assert captured == {
        "base_row": ["1X"],
        "coupon": [],
        "rows": expanded_rows,
        "filter_value": mock_filter_value,
        "reduce_filter": mock_sign_filter,
        "representation_rows": filtered_rows,
        "number_of_matches": 1,
    }


def test_reduce_service_returns_filter_result_without_using_coupon(monkeypatch):
    rows = [mock_filtered_row]

    def fake_append_calculations_to_all_rows(base_row, coupon):
        return rows

    def fake_filter_value_and_row_reductions(rows, filter_value, reduce_filter):
        return rows

    def fake_calculate_sign_representations(rows, number_of_matches):
        return [mock_representation]

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
    monkeypatch.setattr(
        calculation_service,
        "calculate_sign_representations",
        fake_calculate_sign_representations,
    )

    result = calculation_service.reduce_service(["1", "X"], [], None, mock_sign_filter)

    assert result.rows == rows
    assert result.sign_representations == [mock_representation]


def test_reduce_service_with_13_games_passes_rows_to_filter(monkeypatch):
    captured = {}
    rows = [
        Row(signs=["1"], kvot=1.0, people_odds=2.0, market_odds=3.0),
        Row(signs=["X"], kvot=1.0, people_odds=2.0, market_odds=3.0),
        Row(signs=["2"], kvot=1.0, people_odds=2.0, market_odds=3.0),
        Row(signs=["1"], kvot=1.0, people_odds=2.0, market_odds=3.0),
    ]

    def fake_append_calculations_to_all_rows(base_row, coupon):
        captured["base_row"] = base_row
        captured["coupon"] = coupon
        return rows

    def fake_filter_value_and_row_reductions(rows, filter_value, reduce_filter):
        captured["rows"] = rows
        captured["filter_value"] = filter_value
        captured["reduce_filter"] = reduce_filter
        return rows[:3]

    def fake_calculate_sign_representations(rows, number_of_matches):
        captured["representation_rows"] = rows
        captured["number_of_matches"] = number_of_matches
        return [mock_representation]

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
    monkeypatch.setattr(
        calculation_service,
        "calculate_sign_representations",
        fake_calculate_sign_representations,
    )

    result = calculation_service.reduce_service(
        mock_row,
        [],
        mock_filter_value,
        mock_sign_filter,
    )

    assert captured["base_row"] == mock_row
    assert captured["coupon"] == []
    assert captured["rows"] == rows
    assert captured["filter_value"] == mock_filter_value
    assert captured["reduce_filter"] == mock_sign_filter
    assert result.rows == captured["rows"][:3]
    assert result.sign_representations == [mock_representation]
    assert captured["representation_rows"] == captured["rows"][:3]
    assert captured["number_of_matches"] == 13


def test_reduce_service_returns_sign_representations_from_filtered_rows(monkeypatch):
    rows = [
        Row(signs=["1", "X"], kvot=1.0, people_odds=2.0, market_odds=3.0),
        Row(signs=["X", "X"], kvot=1.0, people_odds=2.0, market_odds=3.0),
        Row(signs=["1", "2"], kvot=1.0, people_odds=2.0, market_odds=3.0),
    ]

    monkeypatch.setattr(
        calculation_service,
        "append_calculations_to_all_rows",
        lambda base_row, coupon: rows,
    )
    monkeypatch.setattr(
        calculation_service,
        "filter_value_and_row_reductions",
        lambda all_rows, filter_value, reduce_filter: all_rows,
    )

    result = calculation_service.reduce_service(["1X", "X2"], [], None, None)

    assert result.rows == rows
    assert [
        representation.model_dump() for representation in result.sign_representations
    ] == [
        {"match_no": 1, "sign": "1", "count": 2, "percentage": 66.67},
        {"match_no": 1, "sign": "X", "count": 1, "percentage": 33.33},
        {"match_no": 1, "sign": "2", "count": 0, "percentage": 0.0},
        {"match_no": 2, "sign": "1", "count": 0, "percentage": 0.0},
        {"match_no": 2, "sign": "X", "count": 2, "percentage": 66.67},
        {"match_no": 2, "sign": "2", "count": 1, "percentage": 33.33},
    ]
