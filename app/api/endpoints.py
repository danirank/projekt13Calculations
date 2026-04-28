from fastapi import APIRouter
from app.data.mock_coupon import mock_row

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/rows")
async def items():
    return mock_row