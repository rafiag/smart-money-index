import pytest
import pandas as pd
import plotly.graph_objects as go
from src.dashboard.utils import create_divergence_chart

def test_create_chart_empty_df():
    """Test that empty DataFrame returns empty figure without crashing."""
    df = pd.DataFrame()
    fig = create_divergence_chart(df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0

def test_create_chart_missing_columns():
    """Test that DataFrame missing required columns returns empty figure."""
    # Missing 'institutional_z'
    df = pd.DataFrame({
        "date": [1, 2],
        "retail_search_z": [0.1, 0.2]
    })
    fig = create_divergence_chart(df)
    assert len(fig.data) == 0

def test_create_chart_success():
    """Test valid chart generation."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "retail_search_z": [1.0, 1.2],
        "institutional_z": [-0.5, -0.6],
        "price_z": [0.1, 0.2],
        "price_close": [150, 155]
    })
    
    # Test with all toggles on
    fig = create_divergence_chart(
        df, 
        show_retail=True, 
        show_institutional=True,
        show_price_z=True,
        show_raw_price=True
    )
    
    # Should have 4 traces
    assert len(fig.data) == 4
    
    # Verify names
    names = [trace.name for trace in fig.data]
    assert "Retail Hype (Z-Score)" in names
    assert "Stock Price ($)" in names
