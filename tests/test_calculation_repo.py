from app.models.data_classes import (
    DisagreementOutcomeDto,
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


mock_single_row = ["1", "X", "X", "1", "1", "2", "X", "X", "1", "1", "1", "1", "1"]
mock_single_row2 = ["X", "X", "X", "1", "1", "2", "X", "X", "1", "1", "1", "1", "1"]
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
mock_matches = [
    MatchInfoDto(
        MatchNo=1,
        HomeTeam="IFK Goteborg",
        AwayTeam="Malmo FF",
        Odds1=2.10,
        OddsX=3.40,
        Odds2=3.20,
        FolkPct1=48.0,
        FolkPctX=22.0,
        FolkPct2=30.0,
        FolkOdds1=2.08,
        FolkOddsX=4.55,
        FolkOdds2=3.33,
        OddsPct1=44.5,
        OddsPctX=27.5,
        OddsPct2=28.0,
        Kvot1=1.01,
        KvotX=0.75,
        Kvot2=0.96,
        Disagreement=5.5,
        DisagreementWithOutcome=DisagreementOutcomeDto(outcome="X", value=5.5),
    ),
    MatchInfoDto(
        MatchNo=2,
        HomeTeam="AIK",
        AwayTeam="Hammarby",
        Odds1=2.50,
        OddsX=3.20,
        Odds2=2.80,
        FolkPct1=40.0,
        FolkPctX=30.0,
        FolkPct2=30.0,
        FolkOdds1=2.50,
        FolkOddsX=3.33,
        FolkOdds2=3.33,
        OddsPct1=38.0,
        OddsPctX=30.0,
        OddsPct2=32.0,
        Kvot1=1.00,
        KvotX=0.96,
        Kvot2=0.84,
        Disagreement=2.0,
        DisagreementWithOutcome=DisagreementOutcomeDto(outcome="1", value=2.0),
    ),
    MatchInfoDto(
        MatchNo=3,
        HomeTeam="Djurgarden",
        AwayTeam="Elfsborg",
        Odds1=1.90,
        OddsX=3.60,
        Odds2=4.20,
        FolkPct1=60.0,
        FolkPctX=20.0,
        FolkPct2=20.0,
        FolkOdds1=1.67,
        FolkOddsX=5.00,
        FolkOdds2=5.00,
        OddsPct1=50.0,
        OddsPctX=27.0,
        OddsPct2=23.0,
        Kvot1=1.14,
        KvotX=0.72,
        Kvot2=0.84,
        Disagreement=10.0,
        DisagreementWithOutcome=DisagreementOutcomeDto(outcome="1", value=10.0),
    ),
]


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
    assert getSingleRows(["1X", "12"]) == [
        ("1", "1"),
        ("1", "2"),
        ("X", "1"),
        ("X", "2"),
    ]


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

    assert [row.signs for row in rows] == [
        ["1", "1"],
        ["1", "2"],
        ["X", "1"],
        ["X", "2"],
    ]


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
            MatchNo=1,
            HomeTeam="A",
            AwayTeam="B",
            Odds1=1.0,
            OddsX=1.0,
            Odds2=1.0,
            FolkPct1=1.0,
            FolkPctX=1.0,
            FolkPct2=1.0,
            FolkOdds1=1.0,
            FolkOddsX=1.0,
            FolkOdds2=1.0,
            OddsPct1=1.0,
            OddsPctX=1.0,
            OddsPct2=1.0,
            Kvot1=0.333,
            KvotX=1.0,
            Kvot2=1.0,
            Disagreement=0.0,
            DisagreementWithOutcome=DisagreementOutcomeDto(outcome="1", value=0.0),
        ),
        MatchInfoDto(
            MatchNo=2,
            HomeTeam="C",
            AwayTeam="D",
            Odds1=1.0,
            OddsX=1.0,
            Odds2=1.0,
            FolkPct1=1.0,
            FolkPctX=1.0,
            FolkPct2=1.0,
            FolkOdds1=1.0,
            FolkOddsX=1.0,
            FolkOdds2=1.0,
            OddsPct1=1.0,
            OddsPctX=1.0,
            OddsPct2=1.0,
            Kvot1=1.0,
            KvotX=1.0,
            Kvot2=1.0,
            Disagreement=0.0,
            DisagreementWithOutcome=DisagreementOutcomeDto(outcome="1", value=0.0),
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

    assert [row.signs for row in result] == [["X", "1"], ["X", "2"]]


def test_filter_value_and_row_reductions_applies_group_reductions():
    rows = _small_row_objects()
    reduction = ReductionFilterDto(
        groups=[
            GroupReduction(
                picks=[
                    SignPick(match_no=1, sign="1"),
                    SignPick(match_no=2, sign="2"),
                ],
                min_hits=2,
            )
        ]
    )

    result = filter_value_and_row_reductions(rows, None, reduction)

    assert [row.signs for row in result] == [["1", "2"]]


def test_is_valid_row_returns_true_when_hits_are_within_range():
    assert is_valid_row(mock_single_row, mock_sign_filter.groups[0])


def test_is_valid_row_returns_false_when_hits_exceed_maximum():
    assert not is_valid_row(mock_single_row2, mock_sign_filter.groups[0])
