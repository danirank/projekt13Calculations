from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.data_classes import DisagreementOutcomeDto, MatchInfoDto, to_camel


class SvenskaSpelDrawsResponse(BaseModel):
    """Envelope returned by /draw/1/{product}/draws."""

    draws: list[dict[str, Any]] = Field(default_factory=list)


class NormalizedCouponDto(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    TipType: str
    Week: int
    Turnover: str | None
    BetStop: str | None
    LastUpdated: str | None
    Matches: list[MatchInfoDto]
    DrawNumber: int
    DrawState: str | None = None
    DrawComment: str | None = None
    RowPrice: str | None = None
    SourceData: dict[str, Any]


def _number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"Missing or invalid Svenska Spel value: {field_name}")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip().replace("\u00a0", "").replace(" ", "")
        if "," in normalized and "." in normalized:
            # Source amounts may contain a thousands separator and decimal comma.
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", ".")
        try:
            return float(normalized)
        except ValueError as error:
            raise ValueError(
                f"Invalid numeric Svenska Spel value for {field_name}: {value!r}"
            ) from error
    raise ValueError(f"Invalid Svenska Spel value for {field_name}: {value!r}")


def _path(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _distribution(event: dict[str, Any], outcome: str) -> Any:
    values = _path(event, "betMetrics", "values") or []
    for item in values:
        if item.get("outcome") == outcome:
            return _path(item, "distribution", "distribution")
    return None


def _folk_value(event: dict[str, Any], key: str, outcome: str) -> Any:
    direct = _path(event, "svenskaFolket", key)
    return direct if direct is not None else _distribution(event, outcome)


def _participant_names(event: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    participants = _path(event, "match", "participants") or []
    home = next((p for p in participants if p.get("type") == "home"), None)
    away = next((p for p in participants if p.get("type") == "away"), None)
    if home is None or away is None:
        raise ValueError(
            f"Event {event.get('eventNumber')} must include home and away participants"
        )
    return home, away


def _match(event: dict[str, Any]) -> MatchInfoDto:
    event_number = event.get("eventNumber")
    if not isinstance(event_number, int):
        raise ValueError("Svenska Spel event is missing a numeric eventNumber")

    home, away = _participant_names(event)
    odds_values = _path(event, "odds") or {}
    start_odds = _path(event, "startOdds") or {}
    favourite_odds = _path(event, "favouriteOdds") or {}
    folk = _path(event, "svenskaFolket") or {}
    metrics = _path(event, "betMetrics") or {}
    outcomes = ("1", "X", "2")
    odds = [
        _number(odds_values.get(key), f"event {event_number} odds.{key}")
        for key in ("one", "x", "two")
    ]
    folk_pct = [
        _number(_folk_value(event, key, outcome), f"event {event_number} folk {outcome}")
        for key, outcome in zip(("one", "x", "two"), outcomes)
    ]
    odds_pct = [round(100 / value) if value > 0 else 0 for value in odds]
    folk_odds = [round(100 / value, 2) if value > 0 else 0 for value in folk_pct]
    ratios = [
        round(folk_odds_value / odds_value, 2)
        if folk_pct_value > 0 and odds_value > 0
        else 0
        for folk_odds_value, odds_value, folk_pct_value in zip(
            folk_odds, odds, folk_pct
        )
    ]
    disagreements = [abs(folk - market) for folk, market in zip(folk_pct, odds_pct)]
    largest = max(range(3), key=lambda index: disagreements[index])
    league = _path(event, "match", "league") or {}
    return MatchInfoDto(
        MatchNo=event_number,
        HomeTeam=str(home.get("name") or ""),
        AwayTeam=str(away.get("name") or ""),
        Odds1=odds[0], OddsX=odds[1], Odds2=odds[2],
        FolkPct1=folk_pct[0], FolkPctX=folk_pct[1], FolkPct2=folk_pct[2],
        FolkOdds1=folk_odds[0], FolkOddsX=folk_odds[1], FolkOdds2=folk_odds[2],
        OddsPct1=odds_pct[0], OddsPctX=odds_pct[1], OddsPct2=odds_pct[2],
        Kvot1=ratios[0], KvotX=ratios[1], Kvot2=ratios[2],
        Disagreement=max(disagreements),
        DisagreementWithOutcome=DisagreementOutcomeDto(
            outcome=outcomes[largest], value=disagreements[largest]
        ),
        MatchId=_path(event, "match", "matchId"),
        MatchStart=_path(event, "match", "matchStart"),
        HomeTeamShortName=home.get("shortName"),
        AwayTeamShortName=away.get("shortName"),
        League=league.get("name"),
        Country=_path(league, "country", "name"),
        StartOdds1=_number(start_odds.get("one"), f"event {event_number} startOdds.one")
        if start_odds.get("one") is not None else None,
        StartOddsX=_number(start_odds.get("x"), f"event {event_number} startOdds.x")
        if start_odds.get("x") is not None else None,
        StartOdds2=_number(start_odds.get("two"), f"event {event_number} startOdds.two")
        if start_odds.get("two") is not None else None,
        FavouritePct1=_number(favourite_odds.get("one"), f"event {event_number} favouriteOdds.one")
        if favourite_odds.get("one") is not None else None,
        FavouritePctX=_number(favourite_odds.get("x"), f"event {event_number} favouriteOdds.x")
        if favourite_odds.get("x") is not None else None,
        FavouritePct2=_number(favourite_odds.get("two"), f"event {event_number} favouriteOdds.two")
        if favourite_odds.get("two") is not None else None,
        FolkRefPct1=_number(folk.get("refOne"), f"event {event_number} svenskaFolket.refOne")
        if folk.get("refOne") is not None else None,
        FolkRefPctX=_number(folk.get("refX"), f"event {event_number} svenskaFolket.refX")
        if folk.get("refX") is not None else None,
        FolkRefPct2=_number(folk.get("refTwo"), f"event {event_number} svenskaFolket.refTwo")
        if folk.get("refTwo") is not None else None,
        DistributionDate=folk.get("date") or metrics.get("distributionDate"),
        DistributionRefDate=folk.get("refDate") or metrics.get("distributionRefDate"),
    )


def normalize_draws(
    payload: dict[str, Any], expected_tip_type: str
) -> NormalizedCouponDto:
    canonical_tip_type = {
        "stryktipset": "Stryktipset",
        "europatipset": "Europatipset",
    }.get(expected_tip_type.strip().lower())
    if canonical_tip_type is None:
        raise ValueError("tipType must be stryktipset or europatipset")

    response = SvenskaSpelDrawsResponse.model_validate(payload)
    candidates = [
        draw for draw in response.draws
        if draw.get("productName", "").casefold() == canonical_tip_type.casefold()
        and draw.get("drawState") == "Open"
    ]
    if not candidates:
        raise LookupError(f"No open {canonical_tip_type} draw was returned")
    draw = candidates[0]
    draw_number = draw.get("drawNumber")
    if not isinstance(draw_number, int):
        raise ValueError("Svenska Spel draw is missing a numeric drawNumber")

    close_time = draw.get("regCloseTime")
    if not isinstance(close_time, str):
        raise ValueError("Svenska Spel draw is missing regCloseTime")
    try:
        week_number = datetime.fromisoformat(close_time.replace("Z", "+00:00")).isocalendar().week
    except ValueError as error:
        raise ValueError("Svenska Spel regCloseTime is not a valid ISO timestamp") from error

    events = draw.get("drawEvents")
    if not isinstance(events, list) or not events:
        raise ValueError("Svenska Spel draw has no drawEvents")
    matches = [_match(event) for event in events if isinstance(event, dict)]
    if len(matches) != len(events):
        raise ValueError("Svenska Spel drawEvents contains an invalid event")
    matches.sort(key=lambda match: match.MatchNo)

    turnover = draw.get("currentNetSale")
    folk_dates = [match.DistributionDate for match in matches if match.DistributionDate]
    return NormalizedCouponDto(
        TipType=canonical_tip_type,
        Week=week_number,
        Turnover=str(turnover) if turnover is not None else None,
        BetStop=close_time,
        LastUpdated=max(folk_dates) if folk_dates else None,
        Matches=matches,
        DrawNumber=draw_number,
        DrawState=draw.get("drawState"),
        DrawComment=draw.get("drawComment"),
        RowPrice=str(draw["rowPrice"]) if draw.get("rowPrice") is not None else None,
        SourceData=draw,
    )
