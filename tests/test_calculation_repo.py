from app.data.mock_coupon import (
    mock_filter_value,
    mock_matches,
    mock_row,
    mock_sign_filter,
    mock_single_row,
    mock_single_row2,
)
from app.models.data_classes import (
    FilterValue,
    GroupReduction,
    KvotReduce,
    MarketOddsReduce,
    MatchInfoDto,
    PeopleOddsReduce,
    ReductionFilterDto,
    Row,
    SignPick,
)
from app.repositories.calculation_repo import (
    append_calculations_to_all_rows,
    append_calculations_to_single_row,
    calcNumberOfRows,
    calculateKvotForSingleRow,
    calculateMarketOddsForSingleRow,
    calculatePeopleOddsForSingleRow,
    filter_value_and_row_reductions,
    getSingleRows,
    get_list_of_all_rows_with_values,
    is_valid_row,
)


def _small_matches() -> list[MatchInfoDto]:
    return mock_matches[:2]


def _small_row_objects() -> list[Row]:
    matches = _small_matches()
    return append_calculations_to_all_rows(["1X", "12"], matches)


def test_calc_number_of_rows_counts_all_combinations():
    assert calcNumberOfRows(["1X", "12", "X"]) == 4


def test_calc_number_of_rows_returns_one_for_single_signs():
    assert calcNumberOfRows(["1", "X", "2"]) == 1


def test_get_single_rows_expands_all_permutations():
    assert getSingleRows(["1X", "12"]) == [("1", "1"), ("1", "2"), ("X", "1"), ("X", "2")]


def test_get_single_rows_returns_one_row_for_fixed_input():
    assert getSingleRows(["1", "X"]) == [("1", "X")]


def test_append_calculations_to_single_row_adds_all_derived_values():
    row = append_calculations_to_single_row(("1", "X"), _small_matches())

    assert row == Row(signs=("1", "X"), kvot=0.97, people_odds=6, market_odds=6)


def test_append_calculations_to_single_row_supports_list_input():
    row = append_calculations_to_single_row(["X", "2"], _small_matches())

    assert row.kvot == 0.63
    assert row.people_odds == 15
    assert row.market_odds == 9


def test_append_calculations_to_all_rows_returns_row_objects_for_each_combination():
    rows = append_calculations_to_all_rows(["1X", "12"], _small_matches())

    assert len(rows) == 4
    assert all(isinstance(row, Row) for row in rows)


def test_append_calculations_to_all_rows_preserves_generated_sign_order():
    rows = append_calculations_to_all_rows(["1X", "12"], _small_matches())

    assert [row.signs for row in rows] == [("1", "1"), ("1", "2"), ("X", "1"), ("X", "2")]


def test_get_list_of_all_rows_with_values_maps_each_row_to_a_row_object():
    all_rows = [("1", "1"), ("X", "2")]

    rows = get_list_of_all_rows_with_values(all_rows, _small_matches())

    assert len(rows) == 2
    assert rows[0] == Row(signs=("1", "1"), kvot=1.01, people_odds=5, market_odds=5)


def test_get_list_of_all_rows_with_values_returns_empty_list_for_no_rows():
    assert get_list_of_all_rows_with_values([], _small_matches()) == []


def test_calculate_market_odds_for_single_row_multiplies_selected_market_odds():
    assert calculateMarketOddsForSingleRow(("1", "X"), _small_matches()) == 6


def test_calculate_market_odds_for_single_row_floors_fractional_result():
    assert calculateMarketOddsForSingleRow(("X", "2"), _small_matches()) == 9


def test_calculate_kvot_for_single_row_multiplies_selected_kvot_values():
    assert calculateKvotForSingleRow(("1", "X"), _small_matches()) == 0.97


def test_calculate_kvot_for_single_row_rounds_to_two_decimals():
    matches = [
        MatchInfoDto(
            1,
            "A",
            "B",
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.333,
            1.0,
            1.0,
            0.0,
            None,
        ),
        MatchInfoDto(
            2,
            "C",
            "D",
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.0,
            None,
        ),
    ]

    assert calculateKvotForSingleRow(("1", "1"), matches) == 0.33


def test_calculate_people_odds_for_single_row_multiplies_selected_people_odds():
    assert calculatePeopleOddsForSingleRow(("1", "X"), _small_matches()) == 6


def test_calculate_people_odds_for_single_row_floors_fractional_result():
    assert calculatePeopleOddsForSingleRow(("X", "2"), _small_matches()) == 15


def test_filter_value_and_row_reductions_applies_value_filters():
    rows = _small_row_objects()
    filters = FilterValue(
        Market=MarketOddsReduce(MinOdds=7, MaxOdds=9),
        People=PeopleOddsReduce(MinOdds=6, MaxOdds=15),
        Kvot=KvotReduce(MinKvot=0.63, MaxKvot=0.96),
    )

    result = filter_value_and_row_reductions(rows, filters, None)

    assert [row.signs for row in result] == [("X", "1"), ("X", "2")]


def test_filter_value_and_row_reductions_applies_group_reductions():
    rows = _small_row_objects()
    reduction = ReductionFilterDto(
        groups=[GroupReduction(picks=[SignPick(1, "1"), SignPick(2, "2")], min_hits=2)]
    )

    result = filter_value_and_row_reductions(rows, None, reduction)

    assert [row.signs for row in result] == [("1", "2")]


def test_is_valid_row_returns_true_when_hits_are_within_range():
    assert is_valid_row(mock_single_row, mock_sign_filter.groups[0])


def test_is_valid_row_returns_false_when_hits_exceed_maximum():
    assert not is_valid_row(mock_single_row2, mock_sign_filter.groups[0])
