import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.dashboard.components import render_sidebar

@patch('src.dashboard.components.st')
@patch('src.dashboard.components.get_all_tickers')
def test_render_sidebar_empty_db(mock_get_all_tickers, mock_st):
    """Test that sidebar handles empty database gracefully."""
    # Setup - DB returns empty list
    mock_get_all_tickers.return_value = []
    
    # Run
    result = render_sidebar()
    
    # Assert
    # Should warn user
    mock_st.warning.assert_called_with("No tickers found. Please run data collection.")
    # Should return empty ticker
    assert result["ticker"] is None

@patch('src.dashboard.components.st')
@patch('src.dashboard.components.get_all_tickers')
def test_render_sidebar_with_data(mock_get_all_tickers, mock_st):
    """Test standard sidebar behavior with data."""
    # Setup
    mock_get_all_tickers.return_value = [{"symbol": "AAPL", "name": "Apple Inc"}]
    
    # Explicitly set sidebar to a stable mock to avoid property regeneration issues
    mock_sidebar = MagicMock()
    mock_st.sidebar = mock_sidebar
    mock_sidebar.selectbox.return_value = "AAPL"
    
    # Run
    result = render_sidebar()
    
    # DEBUG: If this fails, we want to know what result['ticker'] actually is
    assert result["ticker"] == "AAPL", f"Expected 'AAPL', got {result['ticker']}"
    
    # Verify date inputs called
    assert mock_st.sidebar.date_input.call_count >= 2
    
    # Check the calls
    calls = mock_st.sidebar.date_input.call_args_list
    args_0, kwargs_0 = calls[0]
    
    assert args_0[0] == "Start Date"
    # Just verify min_value is set and is a datetime object
    assert kwargs_0.get('min_value') is not None
    assert isinstance(kwargs_0.get('min_value'), datetime)
    assert kwargs_0.get('min_value').year == 2024
