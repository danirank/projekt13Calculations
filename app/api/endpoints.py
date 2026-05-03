from unittest import result
from urllib import request

from fastapi import APIRouter
from pydantic import BaseModel
from app.models.data_classes import FilterValue, MatchInfoDto, ReductionFilterDto
from app.services.calculation_service import reduce_service 
router = APIRouter()


@router.get("/")
async def root():
    return {"status": "Api running successfully"}



class ReduceRequest(BaseModel):
    base_row: list[str]
    coupon: list[MatchInfoDto]
    filter_value: FilterValue = FilterValue()
    reduce_filter: ReductionFilterDto | None = None


@router.post("/reduce")
def reduce(request: ReduceRequest):
     return reduce_service(request.base_row, request.coupon, request.filter_value, request.reduce_filter)
    
