"""Integration tests for database operations"""

import tempfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import (
    Base,
    GoogleTrend,
    InsiderTransaction,
    InstitutionalHolding,
    Price,
    Ticker,
    ZScore,
)


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create temporary SQLite database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    engine.dispose()


class TestDatabaseModels:
    """Test database models and relationships"""

    def test_create_ticker(self, test_db):
        """Test creating a ticker"""
        ticker = Ticker(
            symbol="AAPL",
            company_name="Apple Inc."
        )
        test_db.add(ticker)
        test_db.commit()

        # Query back
        result = test_db.query(Ticker).filter(Ticker.symbol == "AAPL").first()

        assert result is not None
        assert result.symbol == "AAPL"
        assert result.company_name == "Apple Inc."
        assert result.ticker_id is not None

    def test_create_price(self, test_db):
        """Test creating price data"""
        # Create ticker first
        ticker = Ticker(symbol="AAPL", company_name="Apple Inc.")
        test_db.add(ticker)
        test_db.flush()

        # Create price
        price = Price(
            ticker_id=ticker.ticker_id,
            date=date(2024, 1, 15),
            open=Decimal("150.25"),
            high=Decimal("152.50"),
            low=Decimal("149.75"),
            close=Decimal("151.80"),
            volume=50000000
        )
        test_db.add(price)
        test_db.commit()

        # Query back
        result = test_db.query(Price).filter(
            Price.ticker_id == ticker.ticker_id
        ).first()

        assert result is not None
        assert result.close == Decimal("151.80")
        assert result.volume == 50000000

    def test_ticker_price_relationship(self, test_db):
        """Test relationship between ticker and prices"""
        # Create ticker with prices
        ticker = Ticker(symbol="MSFT", company_name="Microsoft")
        test_db.add(ticker)
        test_db.flush()

        # Add multiple prices
        for day in range(1, 4):
            price = Price(
                ticker_id=ticker.ticker_id,
                date=date(2024, 1, day),
                close=Decimal(f"{400 + day}.00")
            )
            test_db.add(price)

        test_db.commit()

        # Query ticker and access prices through relationship
        result = test_db.query(Ticker).filter(Ticker.symbol == "MSFT").first()

        assert len(result.prices) == 3
        assert all(p.ticker_id == ticker.ticker_id for p in result.prices)

    def test_institutional_holding(self, test_db):
        """Test creating institutional holding"""
        ticker = Ticker(symbol="NVDA", company_name="NVIDIA")
        test_db.add(ticker)
        test_db.flush()

        holding = InstitutionalHolding(
            ticker_id=ticker.ticker_id,
            filing_date=date(2024, 5, 15),
            quarter_end=date(2024, 3, 31),
            shares_held=1000000,
            market_value=Decimal("500000000.00"),
            ownership_percent=Decimal("5.25")
        )
        test_db.add(holding)
        test_db.commit()

        result = test_db.query(InstitutionalHolding).first()

        assert result.shares_held == 1000000
        assert result.ownership_percent == Decimal("5.25")

    def test_insider_transaction(self, test_db):
        """Test creating insider transaction"""
        ticker = Ticker(symbol="TSLA", company_name="Tesla")
        test_db.add(ticker)
        test_db.flush()

        transaction = InsiderTransaction(
            ticker_id=ticker.ticker_id,
            transaction_date=date(2024, 6, 1),
            shares_traded=50000,
            transaction_type="buy"
        )
        test_db.add(transaction)
        test_db.commit()

        result = test_db.query(InsiderTransaction).first()

        assert result.shares_traded == 50000
        assert result.transaction_type == "buy"

    def test_google_trend(self, test_db):
        """Test creating Google Trends data"""
        ticker = Ticker(symbol="COIN", company_name="Coinbase")
        test_db.add(ticker)
        test_db.flush()

        trend = GoogleTrend(
            ticker_id=ticker.ticker_id,
            date=date(2024, 1, 10),
            search_interest=75
        )
        test_db.add(trend)
        test_db.commit()

        result = test_db.query(GoogleTrend).first()

        assert result.search_interest == 75

    def test_z_score(self, test_db):
        """Test creating Z-score data"""
        ticker = Ticker(symbol="SMCI", company_name="Super Micro Computer")
        test_db.add(ticker)
        test_db.flush()

        zscore = ZScore(
            ticker_id=ticker.ticker_id,
            date=date(2024, 3, 1),
            price_z=Decimal("1.250"),
            institutional_z=Decimal("-0.500"),
            retail_search_z=Decimal("2.100")
        )
        test_db.add(zscore)
        test_db.commit()

        result = test_db.query(ZScore).first()

        assert result.price_z == Decimal("1.250")
        assert result.institutional_z == Decimal("-0.500")

    def test_unique_constraints(self, test_db):
        """Test that unique constraints are enforced"""
        ticker = Ticker(symbol="AAPL", company_name="Apple Inc.")
        test_db.add(ticker)
        test_db.flush()

        # Add first price
        price1 = Price(
            ticker_id=ticker.ticker_id,
            date=date(2024, 1, 1),
            close=Decimal("150.00")
        )
        test_db.add(price1)
        test_db.commit()

        # Try to add duplicate (same ticker + date)
        price2 = Price(
            ticker_id=ticker.ticker_id,
            date=date(2024, 1, 1),
            close=Decimal("151.00")
        )
        test_db.add(price2)

        with pytest.raises(Exception):  # Will raise IntegrityError
            test_db.commit()
