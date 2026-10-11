from functools import reduce
from itertools import product
import math
from collections.abc import Sequence
from app.models.data_classes import (
    FilterValue,
    GroupReduction,
    MatchInfoDto,
    ReductionFilterDto,
    Row,
    SignRepresentationDto,
)


def calc_favorite_odds(matches: list[MatchInfoDto]) -> float:
    product = 1.0
    for match in matches:
        lowest_odds = min(match.Odds1, match.OddsX, match.Odds2)
        product *= lowest_odds
    return round(product, 0)


def calc_people_odds(matches: list[MatchInfoDto]) -> float:
    product = 1.0
    for match in matches:
        lowest_odds = min(match.FolkOdds1, match.FolkOddsX, match.FolkOdds2)
        product *= lowest_odds
    return round(product, 0)


def calc_value_of_favorite(matches: list[MatchInfoDto]) -> float:
    people = calc_people_odds(matches)
    favorite = calc_favorite_odds(matches)

    if favorite == 0:
        return 0.0

    return round(people / favorite, 2)


def calc_number_of_rows(row: list[str]) -> int:
    return reduce(lambda acc, x: acc * len(x), row, 1)


def get_single_rows(row: list[str]) -> list[tuple[str, ...]]:
    splits = [list(item) for item in row]
    single_rows = list(product(*splits))
    return single_rows


def append_calculations_to_single_row(
    signs: Sequence[str], matches: list[MatchInfoDto]
) -> Row:
    kvot = calculate_kvot_for_single_row(signs, matches)
    people = calculate_people_odds_for_single_row(signs, matches)
    market = calculate_market_odds_for_single_row(signs, matches)

    return Row(signs=list(signs), kvot=kvot, people_odds=people, market_odds=market)


def append_calculations_to_all_rows(
    base_row: list[str], matches: list[MatchInfoDto]
) -> list[Row]:
    all_rows = get_single_rows(base_row)
    return [append_calculations_to_single_row(row, matches) for row in all_rows]


def get_list_of_all_rows_with_values(all_rows, matches: list[MatchInfoDto]):
    rows: list[Row] = []
    for row in all_rows:
        rows.append(append_calculations_to_single_row(row, matches))

    return rows


def calculate_market_odds_for_single_row(
    single_row: Sequence[str], matches: list[MatchInfoDto]
) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {"1": match.Odds1, "X": match.OddsX, "2": match.Odds2}
        result *= odds[sign]

    return math.floor(result)


def calculate_kvot_for_single_row(
    single_row: Sequence[str], matches: list[MatchInfoDto]
) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {"1": match.Kvot1, "X": match.KvotX, "2": match.Kvot2}
        result *= odds[sign]

    return round(result, 2)


def calculate_people_odds_for_single_row(
    single_row: Sequence[str], matches: list[MatchInfoDto]
) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {"1": match.FolkOdds1, "X": match.FolkOddsX, "2": match.FolkOdds2}
        result *= odds[sign]

    return math.floor(result)


def apply_value_filters(rows: list[Row], filters: FilterValue) -> list[Row]:
    kvot = filters.Kvot
    market = filters.Market
    people = filters.People

    if kvot.MinKvot is not None:
        rows = [r for r in rows if r.kvot >= kvot.MinKvot]

    if kvot.MaxKvot is not None:
        rows = [r for r in rows if r.kvot <= kvot.MaxKvot]

    if market.MinOdds is not None:
        rows = [r for r in rows if r.market_odds >= market.MinOdds]

    if market.MaxOdds is not None:
        rows = [r for r in rows if r.market_odds <= market.MaxOdds]

    if people.MinOdds is not None:
        rows = [r for r in rows if r.people_odds >= people.MinOdds]

    if people.MaxOdds is not None:
        rows = [r for r in rows if r.people_odds <= people.MaxOdds]

    return rows


def filter_value_and_row_reductions(
    all_rows: list[Row], filters: FilterValue | None, reduce: ReductionFilterDto | None
) -> list[Row]:

    rows: list[Row] = all_rows
    print(f"Rows before filter: {len(rows)}")
    if filters is not None:
        rows = apply_value_filters(rows, filters)

    if reduce is not None:
        for group in reduce.groups:
            rows = [r for r in rows if is_valid_row(r.signs, group)]
    print(f"Rows after filter: {len(rows)}")
    return rows


def calculate_sign_representations(
    rows: list[Row], number_of_matches: int
) -> list[SignRepresentationDto]:
    total_rows = len(rows)
    representations: list[SignRepresentationDto] = []

    for match_index in range(number_of_matches):
        for sign in ["1", "X", "2"]:
            count = sum(1 for row in rows if row.signs[match_index] == sign)
            percentage = round((count / total_rows) * 100, 2) if total_rows > 0 else 0.0
            representations.append(
                SignRepresentationDto(
                    match_no=match_index + 1,
                    sign=sign,
                    count=count,
                    percentage=percentage,
                )
            )

    return representations


def is_valid_row(row: list[str], reduction: GroupReduction) -> bool:
    hits = 0
    for pick in reduction.picks:
        row_sign = row[pick.match_no - 1]

        if row_sign == pick.sign:
            hits += 1

    if reduction.min_hits is not None and hits < reduction.min_hits:
        return False

    if reduction.max_hits is not None and hits > reduction.max_hits:
        return False

    return True
