import json
import logging

import azure.functions as func
from pydantic import BaseModel, Field, ValidationError

from app.models.data_classes import (
    FilterValue,
    MatchInfoDto,
    ReductionFilterDto,
)
from app.services.calculation_service import init_coupon_data, reduce_service


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


class ReduceRequest(BaseModel):
    base_row: list[str] = Field(min_length=1)
    coupon: list[MatchInfoDto] = Field(min_length=1)
    filter_value: FilterValue = Field(default_factory=FilterValue)
    reduce_filter: ReductionFilterDto | None = None


class InitCouponDataRequest(BaseModel):
    coupon: list[MatchInfoDto] = Field(min_length=1)


def _json_response(value, status_code: int = 200) -> func.HttpResponse:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return func.HttpResponse(
        json.dumps(value), status_code=status_code, mimetype="application/json"
    )


def _validation_response(error: ValidationError) -> func.HttpResponse:
    details = [
        {key: item[key] for key in ("loc", "msg", "type")}
        for item in error.errors(include_url=False)
    ]
    return _json_response({"detail": details}, 422)


@app.route(route="", methods=["GET"])
def health(_request: func.HttpRequest) -> func.HttpResponse:
    return _json_response({"status": "Api running successfully"})


@app.route(route="reduce", methods=["POST"])
def reduce(request: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = ReduceRequest.model_validate(request.get_json())
        result = reduce_service(
            payload.base_row,
            payload.coupon,
            payload.filter_value,
            payload.reduce_filter,
        )
        return _json_response(result)
    except ValidationError as error:
        return _validation_response(error)
    except ValueError as error:
        return _json_response({"detail": str(error)}, 400)


@app.route(route="data", methods=["POST"])
def data(request: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = InitCouponDataRequest.model_validate(request.get_json())
        return _json_response(init_coupon_data(payload.coupon))
    except ValidationError as error:
        return _validation_response(error)
    except ValueError as error:
        return _json_response({"detail": str(error)}, 400)


logging.getLogger("azure.functions").setLevel(logging.INFO)
