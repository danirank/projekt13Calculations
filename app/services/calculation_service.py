from app.models.data_classes import (
    CouponDataDto,
    FilterValue,
    MatchInfoDto,
    ReductionFilterDto,
    Row,
)
from app.repositories.calculation_repo import (
    append_calculations_to_all_rows,
    filter_value_and_row_reductions,
    calc_favorite_odds,
    calc_people_odds,
    calc_value_of_favorite,
)


def reduce_service(
    base_row: list[str],
    coupon: list[MatchInfoDto],
    filter_value: FilterValue,
    reduce_filter: ReductionFilterDto,
) -> list[Row]:

    add_value_to_all_rows = append_calculations_to_all_rows(base_row, coupon)

    return filter_value_and_row_reductions(
        add_value_to_all_rows, filter_value, reduce_filter
    )


def init_coupon_data(coupon: list[MatchInfoDto]) -> CouponDataDto:
    return CouponDataDto(
        favorite=calc_favorite_odds(coupon),
        people=calc_people_odds(coupon),
        value=calc_value_of_favorite(coupon),
    )
