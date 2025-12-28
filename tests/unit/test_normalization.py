"""
Unit tests for the ZScoreNormalizer processor.
"""
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from sqlalchemy.orm import Session

from src.processors.normalization import ZScoreNormalizer

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@pytest.fixture
def normalizer(mock_session):
    return ZScoreNormalizer(mock_session)

def test_winsorization(normalizer):
    """Test that extreme values are capped."""
    # Data: 0 to 99 (100 points)
    data = pd.Series(np.arange(100.0))
    # Make extremes
    data.iloc[0] = -5000 # Extreme low
    data.iloc[99] = 5000 # Extreme high
    
    clean = normalizer._winsorize_outliers(data)
    
    # 1st percentile of 0..99 is roughly 0.99
    # 99th percentile is roughly 98.01
    # Check that extremes are gone
    assert clean.iloc[0] > -100  # Should be clipped to ~0
    assert clean.iloc[99] < 1000 # Should be clipped to ~99

def test_skew_detection(normalizer):
    """Test skewness detection logic."""
    # Normal distribution (skew ~ 0)
    normal_dist = pd.Series(np.random.normal(0, 1, 100))
    assert not normalizer._is_skewed(normal_dist)
    
    # Highly skewed (Log-normal or added outlier)
    skewed_dist = pd.Series(np.random.exponential(1, 100))
    # Exponential skew is usually > 1.5? Ideally around 2.
    # Let's force it
    skewed_dist = pd.concat([pd.Series([0]*90), pd.Series([100]*10)], ignore_index=True)
    assert normalizer._is_skewed(skewed_dist)

def test_calculate_mad_zscore(normalizer):
    """Test logic of MAD calculation."""
    # Series: 10, 10, 10, 100 (Outlier)
    # Median = 10.
    # |x - Med| = 0, 0, 0, 90.
    # Median(|...|) = 0.
    # MAD = 0 -> Avoid 0 check -> NaN
    # Let's use something with variance.
    # 10, 12, 11, 100.
    # Median ~ 11.5. 
    # Data is too short for rolling window if window=30.
    # Mock window=3.
    
    data = pd.Series([10, 12, 11, 100, 11, 12], index=pd.date_range('2024-01-01', periods=6))
    result = normalizer._calculate_mad_zscore(data, window=3, min_periods=3)
    
    assert len(result) == 6
    assert np.isnan(result.iloc[1]) # warmup
    assert not np.isnan(result.iloc[-1])

def test_validation_logging(normalizer, caplog):
    """Test that validation warnings are logged."""
    import logging
    caplog.set_level(logging.WARNING)
    
    df = pd.DataFrame({
        'price_z': [1.0, 6.0, 1.0], # 6.0 is extreme (>5)
        'search_z': [np.nan] * 3    # 100% null (>50%)
    })
    
    normalizer._validate_scores(1, df)
    
    assert "extreme price_z values" in caplog.text
    assert "search_z is 100.0% null" in caplog.text

def test_calculate_rolling_zscore_integration(normalizer):
    """Full integration of rolling Z with skew check."""
    # Test valid flow
    data = pd.Series(np.random.normal(0, 1, 100), index=pd.date_range('2024-01-01', periods=100))
    result = normalizer._calculate_rolling_zscore(data, window=30, min_periods=14)
    assert not result.isna().all()
