from pydantic import BaseModel, Field, ConfigDict


def to_camel(string: str) -> str:
    return string[0].lower() + string[1:]


class DisagreementOutcomeDto(BaseModel):
    outcome: str = Field(
        description="Outcome with the largest disagreement between market and people.",
        examples=["1"],
    )
    value: float = Field(
        description="Disagreement value for the selected outcome.",
        examples=[12.5],
    )


class MatchInfoDto(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "matchNo": 1,
                    "homeTeam": "Arsenal",
                    "awayTeam": "Chelsea",
                    "odds1": 2.1,
                    "oddsX": 3.4,
                    "odds2": 3.2,
                    "folkPct1": 58.0,
                    "folkPctX": 22.0,
                    "folkPct2": 20.0,
                    "folkOdds1": 1.72,
                    "folkOddsX": 4.55,
                    "folkOdds2": 5.0,
                    "oddsPct1": 47.62,
                    "oddsPctX": 29.41,
                    "oddsPct2": 31.25,
                    "kvot1": 0.82,
                    "kvotX": 1.34,
                    "kvot2": 1.56,
                    "disagreement": 10.38,
                    "disagreementWithOutcome": {"outcome": "2", "value": 11.25},
                }
            ]
        },
    )

    MatchNo: int = Field(description="One-based match number on the coupon.")
    HomeTeam: str = Field(description="Home team name.")
    AwayTeam: str = Field(description="Away team name.")
    Odds1: float = Field(description="Market odds for home win.")
    OddsX: float = Field(description="Market odds for draw.")
    Odds2: float = Field(description="Market odds for away win.")
    FolkPct1: float = Field(description="People's pick percentage for home win.")
    FolkPctX: float = Field(description="People's pick percentage for draw.")
    FolkPct2: float = Field(description="People's pick percentage for away win.")
    FolkOdds1: float = Field(description="Implied people odds for home win.")
    FolkOddsX: float = Field(description="Implied people odds for draw.")
    FolkOdds2: float = Field(description="Implied people odds for away win.")
    OddsPct1: float = Field(description="Market implied probability for home win.")
    OddsPctX: float = Field(description="Market implied probability for draw.")
    OddsPct2: float = Field(description="Market implied probability for away win.")
    Kvot1: float = Field(description="Value ratio for home win.")
    KvotX: float = Field(description="Value ratio for draw.")
    Kvot2: float = Field(description="Value ratio for away win.")
    Disagreement: float = Field(
        description="Largest absolute difference between market and people percentages."
    )
    DisagreementWithOutcome: DisagreementOutcomeDto = Field(
        description="Outcome and value for the largest disagreement."
    )


class MarketOddsReduce(BaseModel):
    MinOdds: float | None = Field(
        default=None,
        description="Minimum total market odds allowed for a generated row.",
    )
    MaxOdds: float | None = Field(
        default=None,
        description="Maximum total market odds allowed for a generated row.",
    )


class PeopleOddsReduce(BaseModel):
    MinOdds: float | None = Field(
        default=None,
        description="Minimum total people odds allowed for a generated row.",
    )
    MaxOdds: float | None = Field(
        default=None,
        description="Maximum total people odds allowed for a generated row.",
    )


class KvotReduce(BaseModel):
    MinKvot: float | None = Field(
        default=None,
        description="Minimum total value ratio allowed for a generated row.",
    )
    MaxKvot: float | None = Field(
        default=None,
        description="Maximum total value ratio allowed for a generated row.",
    )


class FilterValue(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "Market": {"MinOdds": 0.0, "MaxOdds": 100000.0},
                    "People": {"MinOdds": None, "MaxOdds": None},
                    "Kvot": {"MinKvot": 0.0, "MaxKvot": 100000.0},
                }
            ]
        }
    )

    Market: MarketOddsReduce = Field(
        default_factory=MarketOddsReduce,
        description="Market odds limits for generated rows.",
    )
    People: PeopleOddsReduce = Field(
        default_factory=PeopleOddsReduce,
        description="People odds limits for generated rows.",
    )
    Kvot: KvotReduce = Field(
        default_factory=KvotReduce,
        description="Value ratio limits for generated rows.",
    )


class SignPick(BaseModel):
    match_no: int = Field(description="One-based match number.")
    sign: str = Field(description="Required sign for the match.", examples=["1"])


class GroupReduction(BaseModel):
    picks: list[SignPick] = Field(
        default_factory=list,
        description="Signs included in this reduction group.",
    )
    min_hits: int | None = Field(
        default=None,
        description="Minimum number of group picks that must be present in a row.",
    )
    max_hits: int | None = Field(
        default=None,
        description="Maximum number of group picks that may be present in a row.",
    )


class ReductionFilterDto(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "groups": [
                        {
                            "picks": [
                                {"match_no": 1, "sign": "1"},
                                {"match_no": 2, "sign": "X"},
                                {"match_no": 3, "sign": "2"},
                            ],
                            "min_hits": 1,
                            "max_hits": 2,
                        }
                    ]
                }
            ]
        }
    )

    groups: list[GroupReduction] = Field(
        default_factory=list,
        description="Group-based row reduction rules.",
    )


class Row(BaseModel):
    signs: list[str] = Field(
        description="Selected signs per match for the generated row.",
        examples=[["1", "X", "2"]],
    )
    kvot: float = Field(description="Total value ratio for the row.", examples=[1.42])
    people_odds: float = Field(
        description="Total people odds for the row.",
        examples=[24.7],
    )
    market_odds: float = Field(
        description="Total market odds for the row.",
        examples=[18.3],
    )


class SignRepresentationDto(BaseModel):
    match_no: int = Field(description="One-based match number.", examples=[1])
    sign: str = Field(description="Represented sign.", examples=["1"])
    count: int = Field(
        description="Number of filtered rows containing this sign for the match.",
        examples=[42],
    )
    percentage: float = Field(
        description="Percentage of filtered rows containing this sign for the match.",
        examples=[33.33],
    )


class ReduceResponseDto(BaseModel):
    rows: list[Row] = Field(description="Rows that remain after all reductions.")
    sign_representations: list[SignRepresentationDto] = Field(
        description="Sign distribution per match based on the filtered rows."
    )


class CouponDataDto(BaseModel):
    favorite: float = Field(
        description="Aggregate favorite score for the coupon.",
        examples=[42.5],
    )
    people: float = Field(
        description="Aggregate people percentage score for the coupon.",
        examples=[36.2],
    )
    value: float = Field(
        description="Aggregate value score for the coupon.",
        examples=[21.3],
    )
