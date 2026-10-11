import sys
import json

from app.models.data_classes import (
    FilterValue,
    MatchInfoDto,
    ReductionFilterDto,
)
from app.services.calculation_service import (
    reduce_service,
    init_coupon_data,
)


def reduce(data: dict):
    base_row = data["base_row"]

    coupon = [
        MatchInfoDto.model_validate(match)
        for match in data["coupon"]
    ]

    filter_value = FilterValue.model_validate(
        data.get("filter_value", {})
    )

    reduce_filter_data = data.get("reduce_filter")

    reduce_filter = (
        ReductionFilterDto.model_validate(reduce_filter_data)
        if reduce_filter_data
        else None
    )

    return reduce_service(
        base_row,
        coupon,
        filter_value,
        reduce_filter,
    )


def init_data(data: dict):
    coupon = [
        MatchInfoDto.model_validate(match)
        for match in data["coupon"]
    ]

    return init_coupon_data(coupon)


def main():
    request = json.loads(sys.stdin.read())

    operation = request["operation"]
    data = request["data"]

    if operation == "reduce":
        result = reduce(data)

    elif operation == "data":
        result = init_data(data)

    else:
        raise ValueError(f"Unknown operation: {operation}")

    if hasattr(result, "model_dump"):
        result = result.model_dump(mode="json")

    print(json.dumps(result))


if __name__ == "__main__":
    main()