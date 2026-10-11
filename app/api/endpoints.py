from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field
from app.models.data_classes import (
    CouponDataDto,
    FilterValue,
    MatchInfoDto,
    ReduceResponseDto,
    ReductionFilterDto,
)
from app.services.calculation_service import reduce_service, init_coupon_data

router = APIRouter()

EXAMPLE_MATCH = {
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


class HealthResponse(BaseModel):
    status: str = Field(description="Current service status.")


@router.get(
    "/",
    tags=["health"],
    summary="Check API health",
    description="Returns a lightweight status response when the service is running.",
    response_description="The current API health status.",
    response_model=HealthResponse,
)
async def root():
    return {"status": "Api running successfully"}


class ReduceRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "base_row": [
                        "1X",
                        "1",
                        "X2",
                        "12",
                        "1X2",
                        "2",
                        "X",
                        "1",
                        "1X",
                        "2",
                        "12",
                        "X",
                        "1",
                    ],
                    "coupon": [EXAMPLE_MATCH],
                    "filter_value": {
                        "Market": {"MinOdds": 0.0, "MaxOdds": 100000.0},
                        "People": {"MinOdds": None, "MaxOdds": None},
                        "Kvot": {"MinKvot": 0.0, "MaxKvot": 100000.0},
                    },
                    "reduce_filter": {
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
                    },
                }
            ]
        }
    )

    base_row: list[str] = Field(
        description=(
            "Base selections for each match. Each item can contain one or more "
            "signs, such as '1', 'X', '2', '1X', or '1X2'."
        ),
        min_length=1,
    )
    coupon: list[MatchInfoDto] = Field(
        description="Match data used to calculate odds and value for generated rows.",
        min_length=1,
    )
    filter_value: FilterValue = Field(
        default_factory=FilterValue,
        description="Optional odds and value limits applied to generated rows.",
    )
    reduce_filter: ReductionFilterDto | None = Field(
        default=None,
        description="Optional group reduction rules applied after row generation.",
    )


class InitCouponDataRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "coupon": [EXAMPLE_MATCH],
                }
            ]
        }
    )

    coupon: list[MatchInfoDto] = Field(
        description="Match data used to calculate coupon-level summary values.",
        min_length=1,
    )


@router.post(
    "/reduce",
    tags=["calculations"],
    summary="Reduce coupon rows",
    description=(
        "Expands the base row into all matching sign combinations, calculates "
        "market odds, people odds, and value ratio for each generated row, then "
        "applies the provided value and group reduction filters."
    ),
    response_description="Rows and sign representation after reductions.",
    response_model=ReduceResponseDto,
)
def reduce(request: ReduceRequest):
    return reduce_service(
        request.base_row, request.coupon, request.filter_value, request.reduce_filter
    )


@router.post(
    "/data",
    tags=["calculations"],
    summary="Calculate coupon data",
    description=(
        "Calculates coupon-level summary values for favorite, people, and value "
        "based on the supplied matches."
    ),
    response_description="Coupon-level summary values.",
    response_model=CouponDataDto,
)
def init_data(request: InitCouponDataRequest):
    return init_coupon_data(request.coupon)
