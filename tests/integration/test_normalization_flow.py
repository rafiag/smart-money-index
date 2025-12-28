"""
Integration tests for the normalization pipeline.
Verifies data loading, processing, and persistence using a real (in-memory) database.
"""
import os
import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set ENV to use in-memory DB before importing config/base
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.database.base import Base
from src.database.models import Ticker, Price, GoogleTrend, InstitutionalHolding, ZScore
from src.processors.normalization import ZScoreNormalizer

@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_full_normalization_pipeline(db_session):
    """
    End-to-end test:
    1. Seed DB with Ticker, Prices, Trends, Holdings
    2. Run ZScoreNormalizer
    3. Verify ZScore table population
    """
    # 1. Seed Data
    ticker = Ticker(symbol="TEST", company_name="Test Corp")
    db_session.add(ticker)
    db_session.flush() # get ticker_id
    
    # Generate 120 days of data (enough for quarterly calc + ffill)
    # Start earlier so we have history
    start_date = date(2023, 11, 1) 
    
    for i in range(120):
        current_date = start_date + timedelta(days=i)
        
        # Prices (linear trend for variance)
        price = Price(
            ticker_id=ticker.ticker_id,
            date=current_date,
            close=Decimal(100 + i),
            open=Decimal(100), high=Decimal(110), low=Decimal(90), volume=1000
        )
        db_session.add(price)
        
        # Trends (Weekly - every Monday)
        if current_date.weekday() == 0:
            trend = GoogleTrend(
                ticker_id=ticker.ticker_id,
                date=current_date,
                search_interest=50 + i 
            )
            db_session.add(trend)
        
    # Holdings (Quarterly)
    # 2023-09-30 (Q3)
    h1 = InstitutionalHolding(
        ticker_id=ticker.ticker_id,
        quarter_end=date(2023, 9, 30),
        filing_date=date(2023, 11, 15),
        ownership_percent=Decimal(60.0),
        shares_held=1000000
    )
    db_session.add(h1)
    
    # 2023-12-31 (Q4)
    h2 = InstitutionalHolding(
        ticker_id=ticker.ticker_id,
        quarter_end=date(2023, 12, 31),
        filing_date=date(2024, 2, 14),
        ownership_percent=Decimal(65.0),
        shares_held=1100000
    )
    db_session.add(h2)

    # 2024-03-31 (Q1) - In future relative to some prices, but within 120 days of Nov 1 (ends ~Mar 1)
    # 120 days from Nov 1 is Feb 28.
    # So we have 2 quarters: Sep 30, Dec 31.
    # MIN_PERIODS_HOLDINGS is 2.
    # So Dec 31 should have a Z-Score (comparing Dec 31 vs Sep 31).
    # And it should ffill from Dec 31 onwards (Jan, Feb).
    
    db_session.commit()
    
    # 2. Run Normalizer
    normalizer = ZScoreNormalizer(db_session)
    # Adjust min periods for small test data
    normalizer.MIN_PERIODS_HOLDINGS = 2
    normalizer.MIN_PERIODS_TRENDS = 2
    
    count = normalizer.process_ticker(ticker.ticker_id)
    
    # 3. Verify
    # Prices exist for 120 days.
    # We expect ZScore records aligned to prices.
    assert count == 120
    
    # Check values in DB (Feb 1, 2024)
    target_date = date(2024, 2, 1)
    
    # DEBUG: Dump all ZScores to see what we have
    all_scores = db_session.query(ZScore).filter_by(ticker_id=ticker.ticker_id).all()
    print(f"\nTotal ZScores: {len(all_scores)}")
    for z in all_scores:
        if z.institutional_z is not None:
             print(f"Valid Inst Z at {z.date}: {z.institutional_z}")
    
    z_rec = db_session.query(ZScore).filter_by(ticker_id=ticker.ticker_id, date=target_date).first()
    
    assert z_rec is not None, f"No ZScore found for {target_date}"
    assert z_rec.price_z is not None, f"Price Z is None at {target_date}"
    # Trends (weekly) should be ffilled
    assert z_rec.retail_search_z is not None, "Weekly search trend Z-score was not forward-filled"
    # Holdings (from Dec 31) should be ffilled to Feb 1
    assert z_rec.institutional_z is not None, "Quarterly holdings Z-score was not forward-filled"
