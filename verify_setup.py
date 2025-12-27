#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick verification script to test database setup and basic functionality.

Run this before the full data collection to ensure everything is configured correctly.
"""

import sys
from datetime import datetime

from src.config import get_settings
from src.database import Ticker, get_session, init_db
from src.utils import get_logger, setup_logging

# Set console encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    """Run basic verification checks"""

    setup_logging()
    logger = get_logger(__name__)

    print("="*70)
    print("Smart Money Divergence Index - Setup Verification")
    print("="*70)
    print()

    errors = []

    # 1. Check configuration
    print("1. Checking configuration...")
    try:
        settings = get_settings()
        print(f"   ✓ Environment: {settings.ENVIRONMENT}")
        print(f"   ✓ Database: {settings.DATABASE_URL.split('://')[0]}")
        print(f"   ✓ Data start date: {settings.DATA_START_DATE.date()}")
        print(f"   ✓ Whitelisted tickers: {len(settings.WHITELISTED_TICKERS)}")

        # Try to validate settings
        try:
            settings.validate()
            print(f"   ✓ Configuration validation passed")
        except ValueError as e:
            print(f"   ⚠ Configuration validation warning: {e}")
            print(f"   Note: Reddit credentials may not be set (required for Reddit data collection)")

    except Exception as e:
        errors.append(f"Configuration error: {e}")
        print(f"   ✗ Configuration failed: {e}")

    print()

    # 2. Check database connection
    print("2. Checking database connection...")
    try:
        init_db()
        print(f"   ✓ Database initialized successfully")

        # Try to query database
        with get_session() as session:
            ticker_count = session.query(Ticker).count()
            print(f"   ✓ Database connection working (found {ticker_count} tickers)")

    except Exception as e:
        errors.append(f"Database error: {e}")
        print(f"   ✗ Database connection failed: {e}")

    print()

    # 3. Create test ticker
    print("3. Testing database write...")
    try:
        with get_session() as session:
            # Check if test ticker exists
            test_ticker = session.query(Ticker).filter(
                Ticker.symbol == "TEST"
            ).first()

            if test_ticker:
                print(f"   ✓ Test ticker already exists")
            else:
                # Create test ticker
                test_ticker = Ticker(
                    symbol="TEST",
                    company_name="Test Company Inc."
                )
                session.add(test_ticker)
                session.commit()
                print(f"   ✓ Successfully created test ticker")

            # Clean up test ticker
            session.delete(test_ticker)
            session.commit()
            print(f"   ✓ Successfully deleted test ticker")

    except Exception as e:
        errors.append(f"Database write error: {e}")
        print(f"   ✗ Database write failed: {e}")

    print()

    # 4. Check dependencies
    print("4. Checking critical dependencies...")
    dependencies = [
        ("pandas", "Data manipulation"),
        ("sqlalchemy", "Database ORM"),
        ("yfinance", "Yahoo Finance API"),
        ("praw", "Reddit API"),
        ("pytrends", "Google Trends API"),
        ("textblob", "Sentiment analysis"),
        ("plotly", "Interactive charts"),
        ("streamlit", "Web dashboard"),
    ]

    for package, description in dependencies:
        try:
            __import__(package)
            print(f"   ✓ {package:15s} - {description}")
        except ImportError:
            errors.append(f"Missing dependency: {package}")
            print(f"   ✗ {package:15s} - NOT FOUND")

    print()

    # 5. Summary
    print("="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)

    if errors:
        print(f"\n⚠ Found {len(errors)} issue(s):")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix these issues before running data collection.")
        return 1
    else:
        print("\n✓ All checks passed! Ready for data collection.")
        print("\nNext steps:")
        print("  1. Configure Reddit API credentials in .env file")
        print("  2. Run: python collect_data.py")
        return 0


if __name__ == "__main__":
    sys.exit(main())
