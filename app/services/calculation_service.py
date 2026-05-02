from app.models.data_classes import FilterValue, KvotReduce, MarketOddsReduce, MatchInfoDto, PeopleOddsReduce, ReductionFilterDto
from app.repositories.calculation_repo import calcNumberOfRows, getSingleRows,calculateMarketOddsForSingleRow, calculateKvotForSingleRow, calculatePeopleOddsForSingleRow,filter_value_and_row_reductions,is_valid_row

def reduce_service(base_row: list[str], coupon: list[MatchInfoDto], filter_value: FilterValue , reduce_filter: ReductionFilterDto):
    ## Hämta alla enkelrader
    single_rows = getSingleRows(base_row)

    rows_after_filetr = filter_value_and_row_reductions(single_rows, filter_value, reduce_filter)

    return rows_after_filetr
    
