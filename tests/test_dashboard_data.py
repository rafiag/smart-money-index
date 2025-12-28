import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime
from src.dashboard.data_loader import get_all_tickers, get_ticker_data

@patch('src.dashboard.data_loader.get_session')
def test_get_all_tickers(mock_get_session):
    # Setup mock
    mock_session = MagicMock()
    mock_get_session.return_value.__enter__.return_value = mock_session
    
    # Mock database result
    mock_result = MagicMock()
    mock_result.symbol = "AAPL"
    mock_result.company_name = "Apple Inc."
    mock_session.execute.return_value.all.return_value = [mock_result]

    # Run function
    result = get_all_tickers()
    
    # Assertions
    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["name"] == "Apple Inc."

@patch('src.dashboard.data_loader.get_session')
def test_get_ticker_data(mock_get_session):
    # Setup mock
    mock_session = MagicMock()
    mock_get_session.return_value.__enter__.return_value = mock_session
    
    # Mock Ticker query
    mock_ticker = MagicMock()
    mock_ticker.ticker_id = 1
    mock_session.query.return_value.filter.return_value.first.return_value = mock_ticker

    # Mock Data query result (using raw tuples as SQLAlchemy returns)
    # Columns: date, price_z, institutional_z, retail_search_z, price_close
    mock_rows = [
        (datetime(2024, 1, 1), 0.5, -0.2, 1.5, 150.0),
        (datetime(2024, 1, 2), 0.6, -0.1, 1.6, 155.0)
    ]
    mock_session.execute.return_value.all.return_value = mock_rows

    # Run function
    df = get_ticker_data("AAPL")

    # Assertions
    assert not df.empty
    assert len(df) == 2
    assert "retail_search_z" in df.columns
    assert df.iloc[0]["price_close"] == 150.0
