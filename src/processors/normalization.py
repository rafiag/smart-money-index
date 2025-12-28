"""
Normalization engine for calculating Z-scores across different data types.
Handles data alignment, outlier detection, and statistical normalization.
"""
import logging
from datetime import timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import Session

from src.database.models import (
    Price,
    GoogleTrend,
    InstitutionalHolding,
    ZScore,
    Ticker
)

# Configure logger
logger = logging.getLogger(__name__)

class ZScoreNormalizer:
    """
    Calculates rolling Z-scores for Price, Retail Interest, and Institutional Holdings.
    Uses frequency-specific windows to handle disparate data sources.
    """
    
    # Constants for Window Sizes
    WINDOW_PRICE = 30      # 30 days
    WINDOW_TRENDS = 4      # 4 weeks
    WINDOW_HOLDINGS = 4    # 4 quarters (1 year)
    
    # Minimum periods required
    MIN_PERIODS_PRICE = 14
    MIN_PERIODS_TRENDS = 4
    MIN_PERIODS_HOLDINGS = 2

    # Forward-fill limits (days)
    FFILL_LIMIT_TRENDS = 7      # 1 week buffer for weekly data
    FFILL_LIMIT_HOLDINGS = 95   # ~3 months for quarterly data
    
    # Outlier Thresholds
    SKEW_THRESHOLD = 1.5   # If skew > 1.5, use MAD
    WINSOR_LOWER = 0.01    # 1st percentile
    WINSOR_UPPER = 0.99    # 99th percentile

    def __init__(self, session: Session):
        self.session = session

    def process_ticker(self, ticker_id: int) -> int:
        """
        Full processing pipeline for a single ticker.
        Returns number of records saved.
        """
        # 1. Fetch Raw Data
        prices_df, trends_df, holdings_df = self._fetch_raw_data(ticker_id)
        
        if prices_df.empty or len(prices_df) < self.MIN_PERIODS_PRICE:
            return 0

        # 2. Calculate Z-Scores independently (Frequency-Specific Strategy)
        price_z = self._calculate_rolling_zscore(prices_df['price'], self.WINDOW_PRICE, self.MIN_PERIODS_PRICE)
        trends_z = self._calculate_rolling_zscore(trends_df['search'], self.WINDOW_TRENDS, self.MIN_PERIODS_TRENDS)
        holdings_z = self._calculate_rolling_zscore(holdings_df['holdings'], self.WINDOW_HOLDINGS, self.MIN_PERIODS_HOLDINGS)

        # 3. Merge and Align (Upsample to Daily)
        df = pd.DataFrame(index=prices_df.index)
        df['price_z'] = price_z
        
        if not trends_z.empty:
            # Reindex to daily price dates using forward fill
            df['search_z'] = trends_z.reindex(df.index, method='ffill', limit=self.FFILL_LIMIT_TRENDS)
        else:
            df['search_z'] = np.nan
            
        logger.info(f"Holdings Z (Raw) Count: {len(holdings_z)}")
        if not holdings_z.empty:
            logger.info(f"Holdings Z Head:\n{holdings_z.head()}")
            # Reindex to daily price dates using forward fill
            df['holdings_z'] = holdings_z.reindex(df.index, method='ffill', limit=self.FFILL_LIMIT_HOLDINGS)
            logger.info(f"Holdings Z (Merged) Non-Null: {df['holdings_z'].count()}")
        else:
            logger.warning("Holdings Z is empty!")
            df['holdings_z'] = np.nan
        
        # 4. Save to Database
        self._validate_scores(ticker_id, df)
        records_saved = self._save_scores(ticker_id, df)
        
        return records_saved

    def _fetch_raw_data(self, ticker_id: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Fetches raw data from DB into separate DataFrames with native indices."""
        # Prices
        prices_query = select(Price.date, Price.close).where(
            Price.ticker_id == ticker_id
        ).order_by(Price.date)
        prices = pd.DataFrame(self.session.execute(prices_query).fetchall(), columns=['date', 'price'])
        if not prices.empty:
            prices.set_index('date', inplace=True)
            prices.index = pd.to_datetime(prices.index)
            prices['price'] = prices['price'].astype(float)
            
        # Trends
        trends_query = select(GoogleTrend.date, GoogleTrend.search_interest).where(
            GoogleTrend.ticker_id == ticker_id
        ).order_by(GoogleTrend.date)
        trends = pd.DataFrame(self.session.execute(trends_query).fetchall(), columns=['date', 'search'])
        if not trends.empty:
            trends.set_index('date', inplace=True)
            trends.index = pd.to_datetime(trends.index)
            trends['search'] = trends['search'].astype(float)

        # Holdings
        holdings_query = select(InstitutionalHolding.quarter_end, InstitutionalHolding.ownership_percent).where(
            InstitutionalHolding.ticker_id == ticker_id
        ).order_by(InstitutionalHolding.quarter_end)
        holdings = pd.DataFrame(self.session.execute(holdings_query).fetchall(), columns=['date', 'holdings'])
        if not holdings.empty:
            holdings.set_index('date', inplace=True)
            holdings.index = pd.to_datetime(holdings.index)
            holdings['holdings'] = holdings['holdings'].astype(float)
            
        return prices, trends, holdings

    def _winsorize_outliers(self, series: pd.Series) -> pd.Series:
        """Cap extreme values at defined percentiles."""
        lower = series.quantile(self.WINSOR_LOWER)
        upper = series.quantile(self.WINSOR_UPPER)
        return series.clip(lower, upper)
    
    def _is_skewed(self, series: pd.Series) -> bool:
        """Check if data is highly skewed."""
        if len(series) < 10:
            return False
        return abs(series.skew()) > self.SKEW_THRESHOLD

    def _calculate_mad_zscore(self, series: pd.Series, window: int, min_periods: int) -> pd.Series:
        """
        Calculate Robust Z-Score using Median Absolute Deviation (MAD).
        Robust Z = (x - median) / (1.4826 * MAD)
        """
        rolling = series.rolling(window=window, min_periods=min_periods)
        median = rolling.median()
        
        # MAD = median(|x - median|)
        # Pandas rolling doesn't have MAD built-in easily for windowed calc without apply (slow)
        # Approximation: For MVP, we might stick to simplified MAD if perf is issue.
        # But let's use a lambda.
        # Note: rolling().apply() can be slow on large datasets. 
        # For 12 stocks, it's fine.
        
        def mad_func(x):
            return np.median(np.abs(x - np.median(x)))
            
        mad = rolling.apply(mad_func, raw=True)
        
        # Scale factor for normal distribution consistency
        k = 1.4826 
        
        # Avoid zero division
        mad_scaled = (k * mad).replace(0, np.nan)
        
        z_series = (series - median) / mad_scaled
        return z_series

    def _calculate_rolling_zscore(self, series: pd.Series, window: int, min_periods: int) -> pd.Series:
        """Computes rolling Z-scores with Outlier Handling and Robust Fallback."""
        if series.empty:
            return pd.Series(dtype=float)
            
        # 1. Outlier Detection (Winsorization)
        # We apply this globally to the series before rolling.
        # Alternatively, could apply per window, but global is standard for "cleaning" historical data.
        clean_series = self._winsorize_outliers(series)
        
        # 2. Check Skewness
        # If skewed, use MAD. Else, use Std Dev.
        if self._is_skewed(clean_series):
            return self._calculate_mad_zscore(clean_series, window, min_periods)
            
        # 3. Standard Z-Score
        rolling = clean_series.rolling(window=window, min_periods=min_periods)
        mean = rolling.mean()
        std = rolling.std()
        
        # Handle zero variance
        std = std.replace(0, np.nan)
        
        z_series = (clean_series - mean) / std
        return z_series

    def _validate_scores(self, ticker_id: int, df: pd.DataFrame) -> None:
        """Log warnings for suspicious Z-score patterns."""
        # Check for extreme Z-scores (|Z| > 5)
        for col in ['price_z', 'search_z', 'holdings_z']:
            if col in df:
                # Fillna check to avoid errors
                z_vals = df[col].dropna()
                extreme = z_vals.abs() > 5
                if extreme.any():
                    count = extreme.sum()
                    logger.warning(f"Ticker {ticker_id}: {count} extreme {col} values (|Z| > 5)")

        # Check completeness (>50% null)
        # We only care about rows within the valid tracking period
        if len(df) > 0:
            null_pct = df.isnull().sum() / len(df) * 100
            for col, pct in null_pct.items():
                if pct > 50:
                    logger.warning(f"Ticker {ticker_id}: {col} is {pct:.1f}% null")

    def _save_scores(self, ticker_id: int, df: pd.DataFrame) -> int:
        """Persists Z-scores to the database."""
        delete_stmt = delete(ZScore).where(ZScore.ticker_id == ticker_id)
        self.session.execute(delete_stmt)
        
        z_scores = []
        for date_idx, row in df.iterrows():
            def clean_val(val):
                return None if pd.isna(val) else float(val)
                
            z_score = ZScore(
                ticker_id=ticker_id,
                date=date_idx.date(),
                price_z=clean_val(row.get('price_z')),
                institutional_z=clean_val(row.get('holdings_z')),
                retail_search_z=clean_val(row.get('search_z'))
            )
            z_scores.append(z_score)

        self.session.add_all(z_scores)
        self.session.commit()
        
        return len(z_scores)
