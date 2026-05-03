from app.models.data_classes import FilterValue, KvotReduce, MarketOddsReduce, MatchInfoDto, PeopleOddsReduce, ReductionFilterDto
from app.repositories.calculation_repo import append_calculations_to_all_rows, calcNumberOfRows, getSingleRows,calculateMarketOddsForSingleRow, calculateKvotForSingleRow, calculatePeopleOddsForSingleRow,filter_value_and_row_reductions,is_valid_row

def reduce_service(base_row: list[str], coupon: list[MatchInfoDto], filter_value: FilterValue , reduce_filter: ReductionFilterDto):
    
    add_value_to_all_rows = append_calculations_to_all_rows(base_row, coupon)
    
    return filter_value_and_row_reductions(add_value_to_all_rows, filter_value, reduce_filter)

    
    
