
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
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.database.base import Base
from src.database.models import Ticker, Price, GoogleTrend, InstitutionalHolding, ZScore
from src.processors.normalization import ZScoreNormalizer

def debug_run():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Seed Data
    ticker = Ticker(symbol="TEST", company_name="Test Corp")
    session.add(ticker)
    session.flush()

    start_date = date(2023, 11, 1) # Nov 1
    
    # 120 Days of prices (Nov, Dec, Jan, Feb)
    for i in range(120):
        current_date = start_date + timedelta(days=i)
        price = Price(
            ticker_id=ticker.ticker_id,
            date=current_date,
            close=Decimal(100 + i),
            open=Decimal(100), high=Decimal(110), low=Decimal(90), volume=1000
        )
        session.add(price)

    # Holdings
    # Q3
    h1 = InstitutionalHolding(
        ticker_id=ticker.ticker_id,
        quarter_end=date(2023, 9, 30),
        filing_date=date(2023, 11, 15),
        ownership_percent=Decimal(60.0),
        shares_held=1000000
    )
    session.add(h1)
    
    # Q4
    h2 = InstitutionalHolding(
        ticker_id=ticker.ticker_id,
        quarter_end=date(2023, 12, 31),
        filing_date=date(2024, 2, 14),
        ownership_percent=Decimal(65.0),
        shares_held=1100000
    )
    session.add(h2)

    session.commit()

    # 2. Run Normalizer Logic Manually to inspect
    normalizer = ZScoreNormalizer(session)
    # Test overrides
    normalizer.MIN_PERIODS_HOLDINGS = 2
    normalizer.MIN_PERIODS_TRENDS = 2
    
    print("\n--- Fetching Data ---")
    prices, trends, holdings = normalizer._fetch_raw_data(ticker.ticker_id)
    print("Holdings Raw:")
    print(holdings)

    print("\n--- Calculating Z-Scores ---")
    # Window 4, Min 2
    holdings_z = normalizer._calculate_rolling_zscore(
        holdings['holdings'], 
        normalizer.WINDOW_HOLDINGS, 
        normalizer.MIN_PERIODS_HOLDINGS
    )
    print("Holdings Z-Score Series:")
    print(holdings_z)

    print("\n--- Merging ---")
    df = pd.DataFrame(index=prices.index)
    # df['price_z'] = ... (skip for brevity)

    if not holdings_z.empty:
        print("Merging Holdings Z...")
        # Rename for join
        hz_renamed = holdings_z.rename('holdings_z')
        print(hz_renamed)
        
        # JOIN
        df = df.join(hz_renamed, how='left')
        
        print("After Join (around Dec 31):")
        # Check Dec 31
        target = pd.Timestamp('2023-12-31')
        print(df.loc[target - timedelta(days=2) : target + timedelta(days=2), ['holdings_z']])
        
        # FFILL
        df['holdings_z'] = df['holdings_z'].ffill(limit=95)
        
        print("After Ffill (Feb 1):")
        target_feb = pd.Timestamp('2024-02-01')
        print(df.loc[target_feb, ['holdings_z']])
    else:
        print("Holdings Z Empty!")

if __name__ == "__main__":
    debug_run()
