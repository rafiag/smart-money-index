#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified script to generate and verify mock data for the 4-source architecture.
Consolidates generation and verification logic for a cleaner project structure.
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_settings
from src.database import (
    get_session, 
    init_db, 
    Ticker, 
    Price, 
    InstitutionalHolding, 
    InsiderTransaction, 
    GoogleTrend
)
from src.utils.mock_data_generator import MockDataGenerator

def print_summary():
    """Print a summary of the data in the database (from verify_mock_data.py)"""
    settings = get_settings()
    
    print("\n" + "=" * 70)
    print("Database Content Verification Report")
    print("=" * 70)

    with get_session() as session:
        tickers = session.query(Ticker).all()
        print(f"\n[TICKERS] Tickers in Database: {len(tickers)} / {len(settings.WHITELISTED_TICKERS)}")

        for ticker in tickers:
            symbol = ticker.symbol
            print(f"\n[DATA] {symbol} - {ticker.company_name}")

            # Counts for each data pillar
            price_count = session.query(Price).filter_by(ticker_id=ticker.ticker_id).count()
            holdings_count = session.query(InstitutionalHolding).filter_by(ticker_id=ticker.ticker_id).count()
            insider_count = session.query(InsiderTransaction).filter_by(ticker_id=ticker.ticker_id).count()
            trends_count = session.query(GoogleTrend).filter_by(ticker_id=ticker.ticker_id).count()

            print(f"   - Price Records:            {price_count}")
            print(f"   - Institutional Holdings:   {holdings_count}")
            print(f"   - Insider Transactions:     {insider_count}")
            print(f"   - Google Trends:            {trends_count}")

        print("\n" + "=" * 70)
        print("✓ Generation and Verification Complete!")
        print("=" * 70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Generate mock data for the dashboard.")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before generating")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("Smart Money Divergence Index - Unified Mock Data Tool")
    print("=" * 70)

    # Initialize DB
    init_db()
    generator = MockDataGenerator()

    if args.clear:
        generator.clear_all_mock_data()

    print("\nGenerating mock data for all 12 tickers...")
    print("This includes Price, Google Trends, 13F Holdings, and Form 4 Transactions.")
    
    # Generate data
    generator.generate_all_mock_data()

    # Verify results
    print_summary()

    print("Next Steps:")
    print("  1. Run: streamlit run src/dashboard/app.py")
    print("  2. Visit: http://localhost:8501\n")

if __name__ == "__main__":
    main()
