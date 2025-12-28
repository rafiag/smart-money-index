"""
Data Loader for Dashboard
Handles database connections and data fetching logic.
"""
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.base import get_session
from src.database.models import Ticker, ZScore, Price

from src.dashboard.config import CACHE_TTL

@st.cache_data(ttl=CACHE_TTL)
def get_all_tickers():
    """Fetch all available tickers from the database."""
    with get_session() as session:
        stmt = select(Ticker.symbol, Ticker.company_name).order_by(Ticker.symbol)
        results = session.execute(stmt).all()
        return [{"symbol": r.symbol, "name": r.company_name} for r in results]

@st.cache_data(ttl=CACHE_TTL)
def get_ticker_data(ticker_symbol: str, start_date=None, end_date=None):
    """
    Fetch joined Z-Score and Price data for a specific ticker.
    Returns a pandas DataFrame.
    """
    if start_date is None:
        start_date = datetime(2024, 1, 1)
    if end_date is None:
        end_date = datetime.now()

    with get_session() as session:
        # Standardized query style using select()
        stmt_ticker = select(Ticker.ticker_id).where(Ticker.symbol == ticker_symbol)
        ticker_id = session.execute(stmt_ticker).scalar_one_or_none()
        
        if not ticker_id:
            return pd.DataFrame()

        # Query Z-Scores joined with Prices
        stmt = (
            select(
                ZScore.date,
                ZScore.price_z,
                ZScore.institutional_z,
                ZScore.retail_search_z,
                Price.close.label("price_close")
            )
            .join(Price, (ZScore.ticker_id == Price.ticker_id) & (ZScore.date == Price.date), isouter=True)
            .where(
                ZScore.ticker_id == ticker_id,
                ZScore.date >= start_date,
                ZScore.date <= end_date
            )
            .order_by(ZScore.date)
        )
        
        result = session.execute(stmt).all()
        
        if not result:
            return pd.DataFrame()

        df = pd.DataFrame(result, columns=[
            "date", "price_z", "institutional_z", "retail_search_z", "price_close"
        ])
        df["date"] = pd.to_datetime(df["date"])
        return df

def get_ticker_metadata(ticker_symbol: str):
    """Fetch metadata for a single ticker."""
    with get_session() as session:
        stmt = select(Ticker).where(Ticker.symbol == ticker_symbol)
        ticker = session.execute(stmt).scalar_one_or_none()
        if ticker:
            return {"symbol": ticker.symbol, "name": ticker.company_name}
        return None
