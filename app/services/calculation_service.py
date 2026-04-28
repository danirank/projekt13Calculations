from functools import reduce
from itertools import product
import math
from app.models.data_classes import GroupReduction, KvotReduce, MarketOddsReduce, MatchInfoDto, PeopleOddsReduce

def calcNumberOfRows(row: list[str]):
    return reduce(lambda acc, x: acc * len(x), row, 1)


def getSingleRows(row: list[str]):
    splits = [list(item) for item in row]
    single_rows = list(product(*splits))
    return single_rows

def calculateMarketOddsForSingleRow(single_row: tuple[str,...], matches: list[MatchInfoDto]) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {
            "1": match.Odds1,
            "X": match.OddsX,
            "2": match.Odds2
        }
        result *= odds[sign]

    return math.floor(result)

def calculateKvotForSingleRow(single_row: tuple[str,...], matches: list[MatchInfoDto]) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {
            "1": match.Kvot1,
            "X": match.KvotX,
            "2": match.Kvot2
        }
        result *= odds[sign]

    return round(result,2)


def calculatePeopleOddsForSingleRow(single_row: tuple[str,...], matches: list[MatchInfoDto]) -> float:
    result = 1.0

    for match, sign in zip(matches, single_row):
        odds = {
            "1": match.FolkOdds1,
            "X": match.FolkOddsX,
            "2": match.FolkOdds2
        }
        result *= odds[sign]

    return math.floor(result)
            

def filterRowsByOddsAndKvot(all_rows, filters, matches):
    result = []

    for row in all_rows:
        kvot = calculateKvotForSingleRow(row, matches)
        market = calculateMarketOddsForSingleRow(row, matches)
        people = calculatePeopleOddsForSingleRow(row, matches)

        if all(
            not (
                (isinstance(f, KvotReduce) and (
                    (f.MinKvot and kvot < f.MinKvot) or
                    (f.MaxKvot and kvot > f.MaxKvot)
                )) or
                (isinstance(f, MarketOddsReduce) and (
                    (f.MinOdds and market < f.MinOdds) or
                    (f.MaxOdds and market > f.MaxOdds)
                )) or
                (isinstance(f, PeopleOddsReduce) and (
                    (f.MinOdds and people < f.MinOdds) or
                    (f.MaxOdds and people > f.MaxOdds)
                ))
            )
            for f in filters
        ):
            result.append(row)

    return result
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