from app.data.mock_coupon import mock_single_row, mock_sign_filter, mock_single_row2, mock_matches, mock_row, mock_filter_value
from app.repositories.calculation_repo import is_valid_row, filter_value_and_row_reductions, getSingleRows


def test_is_valid_row():
    assert is_valid_row(mock_single_row, mock_sign_filter.groups[0])


def test_is_not_valid_row():
    assert not is_valid_row(mock_single_row2, mock_sign_filter.groups[0])



def test_filter_odds_and_value(): 
    base_row = mock_row
    single_rows  = getSingleRows(base_row)
    filter_value = mock_filter_value
    matches = mock_matches

    result = filter_value_and_row_reductions(single_rows, filter_value, matches, mock_sign_filter )
    
    assert result.count < 8
    assert result.count > 0


