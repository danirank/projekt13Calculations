from app.services.calculation_service import calcNumberOfRows, getSingleRows
from app.data.mock_coupon import mock_row


def test_calcNumberOfRows():
    assert calcNumberOfRows(mock_row) == 8


def test_getAllSingleRows():
    assert len(getSingleRows(mock_row)) == 8
