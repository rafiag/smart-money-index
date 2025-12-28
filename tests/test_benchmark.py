import pytest
import time
import pandas as pd
from src.dashboard.utils import create_divergence_chart

def test_chart_rendering_speed():
    """Verify chart rendering is under 500ms constraint."""
    # Generate larger dataset (365 days)
    dates = pd.date_range(start="2024-01-01", periods=365)
    df = pd.DataFrame({
        "date": dates,
        "retail_search_z": [0.1] * 365,
        "institutional_z": [0.1] * 365,
        "price_z": [0.1] * 365,
        "price_close": [100.0] * 365
    })
    
    start_time = time.time()
    _ = create_divergence_chart(df, True, True, True, True)
    end_time = time.time()
    
    duration = end_time - start_time
    # Assert faster than 500ms
    assert duration < 0.5, f"Chart rendering took {duration:.4f}s (Max 0.5s)"
