from app.data.mock_coupon import mock_single_row, mock_sign_filter, mock_single_row2
from app.services.calculation_service import is_valid_row


def test_is_valid_row():
    assert is_valid_row(mock_single_row, mock_sign_filter.groups[0])


def test_is_not_valid_row():
    assert not is_valid_row(mock_single_row2, mock_sign_filter.groups[0])
