from dataclasses import dataclass

@dataclass
class DisagreementOutcomeDto:
    outcome: str
    value: float
@dataclass
class MatchInfoDto:
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

@dataclass 
class MarketOddsReduce:
    MinOdds: float | None = None
    MaxOdds: float | None = None


@dataclass 
class PeopleOddsReduce:
    MinOdds: float | None = None
    MaxOdds: float | None = None


@dataclass 
class KvotReduce:
    MinKvot: float | None = None
    MaxKvot: float | None = None




@dataclass
class SignPick:
    match_no: int
    sign: str


@dataclass
class GroupReduction:
    picks: list[SignPick]
    min_hits: int | None = None
    max_hits: int | None = None


@dataclass
class ReductionFilterDto:
    groups: list[GroupReduction]