"""SQLAlchemy ORM models for Smart Money Divergence Index database schema"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class Ticker(Base):
    """Stock ticker symbols and company information"""

    __tablename__ = "tickers"

    ticker_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    prices = relationship("Price", back_populates="ticker", cascade="all, delete-orphan")
    institutional_holdings = relationship(
        "InstitutionalHolding", back_populates="ticker", cascade="all, delete-orphan"
    )
    insider_transactions = relationship(
        "InsiderTransaction", back_populates="ticker", cascade="all, delete-orphan"
    )
    google_trends = relationship(
        "GoogleTrend", back_populates="ticker", cascade="all, delete-orphan"
    )
    z_scores = relationship("ZScore", back_populates="ticker", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticker(symbol='{self.symbol}', company='{self.company_name}')>"


class Price(Base):
    """Daily OHLCV price data from Yahoo Finance"""

    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("ticker_id", "date", name="uq_price_ticker_date"),
        Index("idx_prices_ticker_date", "ticker_id", "date"),
    )

    price_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey("tickers.ticker_id"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(DECIMAL(10, 2))
    high = Column(DECIMAL(10, 2))
    low = Column(DECIMAL(10, 2))
    close = Column(DECIMAL(10, 2))
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ticker = relationship("Ticker", back_populates="prices")

    def __repr__(self):
        return f"<Price(ticker_id={self.ticker_id}, date={self.date}, close={self.close})>"


class InstitutionalHolding(Base):
    """SEC Form 13F institutional holdings data"""

    __tablename__ = "institutional_holdings"
    __table_args__ = (
        UniqueConstraint("ticker_id", "quarter_end", name="uq_holding_ticker_quarter"),
        Index("idx_institutional_ticker_quarter", "ticker_id", "quarter_end"),
    )

    holding_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey("tickers.ticker_id"), nullable=False)
    filing_date = Column(Date, nullable=False)
    quarter_end = Column(Date, nullable=False)
    shares_held = Column(BigInteger)
    market_value = Column(DECIMAL(15, 2))
    ownership_percent = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ticker = relationship("Ticker", back_populates="institutional_holdings")

    def __repr__(self):
        return f"<InstitutionalHolding(ticker_id={self.ticker_id}, quarter={self.quarter_end}, shares={self.shares_held})>"


class InsiderTransaction(Base):
    """SEC Form 4 insider transaction data"""

    __tablename__ = "insider_transactions"
    __table_args__ = (Index("idx_insider_ticker_date", "ticker_id", "transaction_date"),)

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey("tickers.ticker_id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    shares_traded = Column(BigInteger)
    transaction_type = Column(String(20))  # 'buy' or 'sell'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ticker = relationship("Ticker", back_populates="insider_transactions")

    def __repr__(self):
        return f"<InsiderTransaction(ticker_id={self.ticker_id}, date={self.transaction_date}, type={self.transaction_type})>"


class GoogleTrend(Base):
    """Google Trends search interest data"""

    __tablename__ = "google_trends"
    __table_args__ = (
        UniqueConstraint("ticker_id", "date", name="uq_trend_ticker_date"),
        Index("idx_trends_ticker_date", "ticker_id", "date"),
    )

    trend_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey("tickers.ticker_id"), nullable=False)
    date = Column(Date, nullable=False)
    search_interest = Column(Integer)  # 0-100 scale
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ticker = relationship("Ticker", back_populates="google_trends")

    def __repr__(self):
        return f"<GoogleTrend(ticker_id={self.ticker_id}, date={self.date}, interest={self.search_interest})>"




class ZScore(Base):
    """Calculated Z-scores for normalized comparisons"""

    __tablename__ = "z_scores"
    __table_args__ = (
        UniqueConstraint("ticker_id", "date", name="uq_zscore_ticker_date"),
        Index("idx_zscores_ticker_date", "ticker_id", "date"),
    )

    z_score_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey("tickers.ticker_id"), nullable=False)
    date = Column(Date, nullable=False)
    price_z = Column(DECIMAL(6, 3))
    institutional_z = Column(DECIMAL(6, 3))
    retail_search_z = Column(DECIMAL(6, 3))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ticker = relationship("Ticker", back_populates="z_scores")

    def __repr__(self):
        return f"<ZScore(ticker_id={self.ticker_id}, date={self.date})>"
