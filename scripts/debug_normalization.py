
import os
import sys
import pandas as pd
import numpy as np
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.getcwd())

# Set ENV
# Set ENV - Removed to use real DB from .env or default
# os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.database.base import Base
from src.database.models import Ticker, Price, GoogleTrend, InstitutionalHolding, ZScore
from src.processors.normalization import ZScoreNormalizer

def debug_run():
    # Connect to REAL DB
    from src.config import get_settings
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Connected to {settings.DATABASE_URL}")

    # 1. Fetch AAPL
    ticker = session.query(Ticker).filter_by(symbol="AAPL").first()
    if not ticker:
        print("AAPL not found!")
        return

    print(f"Processing {ticker.symbol}...")

    # 2. Run Normalizer Logic Manually to inspect
    normalizer = ZScoreNormalizer(session)
    
    print("\n--- Fetching Data ---")
    prices, trends, holdings = normalizer._fetch_raw_data(ticker.ticker_id)
    print("Holdings Raw:")
    print(holdings)

    if holdings.empty:
        print("Holdings RAW IS EMPTY!")

    print("\n--- Calculating Z-Scores ---")
    # Window 4, Min 2
    holdings_z = normalizer._calculate_rolling_zscore(
        holdings['holdings'], 
        normalizer.WINDOW_HOLDINGS, 
        normalizer.MIN_PERIODS_HOLDINGS
    )
    print("Holdings Z-Score Series:")
    print(holdings_z)

    print(f"Holdings Z Non-Null Count: {holdings_z.count()}")
    if holdings_z.count() == 0:
        print("All Z-Scores are NaN! Checking variance...")
        print(f"Rolling Std: {holdings['holdings'].rolling(4, min_periods=2).std()}") 

    print("\n--- Merging ---")
    df = pd.DataFrame(index=prices.index)
    
    if not holdings_z.empty:
        print("Merging Holdings Z...")
        # Reindex
        reindexed = holdings_z.reindex(df.index, method='ffill', limit=95)
        print("Reindexed Sample:")
        print(reindexed.dropna().head())
        print(f"Reindexed Non-Null: {reindexed.count()}")
    else:
        print("Holdings Z Empty!")

if __name__ == "__main__":
    debug_run()
