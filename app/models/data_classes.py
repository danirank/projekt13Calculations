from pydantic import BaseModel, Field


class DisagreementOutcomeDto(BaseModel):
    outcome: str
    value: float


class MatchInfoDto(BaseModel):
    MatchNo: int
    HomeTeam: str
    AwayTeam: str
    Odds1: float
    OddsX: float
    Odds2: float
    FolkPct1: float
    FolkPctX: float
    FolkPct2: float
    FolkOdds1: float
    FolkOddsX: float
    FolkOdds2: float
    OddsPct1: float
    OddsPctX: float
    OddsPct2: float
    Kvot1: float
    KvotX: float
    Kvot2: float
    Disagreement: float
    DisagreementWithOutcome: DisagreementOutcomeDto


class MarketOddsReduce(BaseModel):
    MinOdds: float | None = None
    MaxOdds: float | None = None


class PeopleOddsReduce(BaseModel):
    MinOdds: float | None = None
    MaxOdds: float | None = None


class KvotReduce(BaseModel):
    MinKvot: float | None = None
    MaxKvot: float | None = None


class FilterValue(BaseModel):
    Market: MarketOddsReduce = Field(default_factory=MarketOddsReduce)
    People: PeopleOddsReduce = Field(default_factory=PeopleOddsReduce)
    Kvot: KvotReduce = Field(default_factory=KvotReduce)


class SignPick(BaseModel):
    match_no: int
    sign: str


class GroupReduction(BaseModel):
    picks: list[SignPick] = Field(default_factory=list)
    min_hits: int | None = None
    max_hits: int | None = None


class ReductionFilterDto(BaseModel):
    groups: list[GroupReduction] = Field(default_factory=list)


class Row(BaseModel):
    signs: list[str]
    kvot: float
    people_odds: float
    market_odds: float


class ReduceRequest(BaseModel):
    base_row: list[str]
    coupon: list[MatchInfoDto]
    filter_value: FilterValue = Field(default_factory=FilterValue)
    reduce_filter: ReductionFilterDto = Field(default_factory=ReductionFilterDto)
