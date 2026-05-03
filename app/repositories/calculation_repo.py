from functools import reduce
from itertools import product
import math
from app.models.data_classes import (
    FilterValue,
    GroupReduction,
    MatchInfoDto,
    ReductionFilterDto,
    Row,
)


def calcNumberOfRows(row: list[str]):
    return reduce(lambda acc, x: acc * len(x), row, 1)


def getSingleRows(row: list[str]):
    splits = [list(item) for item in row]
    single_rows = list(product(*splits))
    return single_rows


def append_calculations_to_single_row(
    signs: list[str], matches: list[MatchInfoDto]
) -> Row:
    kvot = calculateKvotForSingleRow(signs, matches)
    people = calculatePeopleOddsForSingleRow(signs, matches)
    market = calculateMarketOddsForSingleRow(signs, matches)

    return Row(signs=signs, kvot=kvot, people_odds=people, market_odds=market)


def append_calculations_to_all_rows(
    base_row: list[str], matches: list[MatchInfoDto]
) -> list[Row]:
    all_rows = getSingleRows(base_row)
    return [append_calculations_to_single_row(row, matches) for row in all_rows]


def get_list_of_all_rows_with_values(all_rows, matches: list[MatchInfoDto]):
    rows: list[Row] = []
    for row in all_rows:
        rows.append(append_calculations_to_single_row(row, matches))

    return rows


def calculateMarketOddsForSingleRow(
    single_row: tuple[str, ...], matches: list[MatchInfoDto]
) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {"1": match.Odds1, "X": match.OddsX, "2": match.Odds2}
        result *= odds[sign]

    return math.floor(result)


def calculateKvotForSingleRow(
    single_row: tuple[str, ...], matches: list[MatchInfoDto]
) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {"1": match.Kvot1, "X": match.KvotX, "2": match.Kvot2}
        result *= odds[sign]

    return round(result, 2)


def calculatePeopleOddsForSingleRow(
    single_row: tuple[str, ...], matches: list[MatchInfoDto]
) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {"1": match.FolkOdds1, "X": match.FolkOddsX, "2": match.FolkOdds2}
        result *= odds[sign]

    return math.floor(result)


def filter_value_and_row_reductions(
    all_rows: list[Row], filters: FilterValue, reduce: ReductionFilterDto | None
) -> list[Row]:

    rows: list[Row] = all_rows
    print(f"Rows before filter: {len(rows)}")
    if filters is not None:
        kvot = filters.Kvot
        market = filters.Market
        people = filters.People

        if kvot.MinKvot is not None:
            rows = [r for r in rows if r.kvot >= filters.Kvot.MinKvot]

        if kvot.MaxKvot is not None:
            rows = [r for r in rows if r.kvot <= filters.Kvot.MaxKvot]

        if market.MinOdds is not None:
            rows = [r for r in rows if r.market_odds >= filters.Market.MinOdds]

        if market.MaxOdds is not None:
            rows = [r for r in rows if r.market_odds <= filters.Market.MaxOdds]

        if people.MinOdds is not None:
            rows = [r for r in rows if r.people_odds >= filters.People.MinOdds]

        if people.MaxOdds is not None:
            rows = [r for r in rows if r.people_odds <= filters.People.MaxOdds]

    if reduce is not None:
        for group in reduce.groups:
            rows = [r for r in rows if is_valid_row(r.signs, group)]
    print(f"Rows after filter: {len(rows)}")
    return rows


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
