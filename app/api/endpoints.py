from fastapi import APIRouter
from pydantic import BaseModel
from app.models.data_classes import CouponDataDto, FilterValue, MatchInfoDto, ReductionFilterDto, Row
from app.services.calculation_service import reduce_service, init_coupon_data

router = APIRouter()


@router.get("/")
async def root():
    return {"status": "Api running successfully"}


class ReduceRequest(BaseModel):
    base_row: list[str]
    coupon: list[MatchInfoDto]
    filter_value: FilterValue = FilterValue()
    reduce_filter: ReductionFilterDto | None = None

class InitCouponDataRequest(BaseModel):
    coupon: list[MatchInfoDto]


@router.post("/reduce", response_model=list[Row])
def reduce(request: ReduceRequest):
    return reduce_service(
        request.base_row, request.coupon, request.filter_value, request.reduce_filter
    )


@router.post("/data", response_model=CouponDataDto)
def init_data(request: InitCouponDataRequest):
    return init_coupon_data(request.coupon)