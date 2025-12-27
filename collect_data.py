#!/usr/bin/env python
"""
Main data collection orchestrator script.

Runs all data collectors sequentially for Phase 1 MVP.
"""

import sys
from datetime import datetime

from src.collectors import (
    Form13FCollector,
    Form4Collector,
    GoogleTrendsCollector,
    PriceCollector,
)
from src.config import get_settings
from src.database import init_db
from src.utils import get_logger, setup_logging
from src.validators import DataValidator


def main():
    """Main orchestrator function"""

    # Setup logging
    setup_logging()
    logger = get_logger(__name__)

    logger.info("="*70)
    logger.info("Smart Money Divergence Index - Data Collection")
    logger.info("="*70)

    try:
        # Load and validate settings
        settings = get_settings()
        settings.validate()

        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Database: {settings.DATABASE_URL.split('://')[0]}")
        logger.info(f"Data range: {settings.DATA_START_DATE.date()} to {datetime.now().date()}")

        # Initialize database
        logger.info("\nInitializing database...")
        init_db()
        logger.info("Database initialized successfully")

        # Collection start and end dates
        start_date = settings.DATA_START_DATE
        end_date = datetime.now()

        # Track overall results
        all_results = {}

        # 1. Collect Price Data (most reliable, run first)
        logger.info("\n" + "="*70)
        logger.info("STEP 1: Collecting Price Data (Yahoo Finance)")
        logger.info("="*70)
        try:
            price_collector = PriceCollector()
            price_results = price_collector.collect_all_tickers(start_date, end_date)
            all_results['prices'] = price_results
            logger.info(f"Price collection complete. Total records: {sum(price_results.values())}")
        except Exception as e:
            logger.error(f"Price collection failed: {e}", exc_info=True)
            all_results['prices'] = {}

        # 2. Collect Google Trends Data
        logger.info("\n" + "="*70)
        logger.info("STEP 2: Collecting Google Trends Data")
        logger.info("="*70)
        try:
            trends_collector = GoogleTrendsCollector()
            trends_results = trends_collector.collect_all_tickers(start_date, end_date)
            all_results['google_trends'] = trends_results
            logger.info(f"Google Trends collection complete. Total records: {sum(trends_results.values())}")
        except Exception as e:
            logger.error(f"Google Trends collection failed: {e}", exc_info=True)
            all_results['google_trends'] = {}

        # 3. Collect SEC 13F Data (Institutional Holdings)
        logger.info("\n" + "="*70)
        logger.info("STEP 3: Collecting SEC 13F Data (Institutional Holdings)")
        logger.info("="*70)
        try:
            form13f_collector = Form13FCollector()
            form13f_results = form13f_collector.collect_all_tickers(start_date, end_date)
            all_results['institutional_holdings'] = form13f_results
            logger.info(f"13F collection complete. Total records: {sum(form13f_results.values())}")
        except Exception as e:
            logger.error(f"13F collection failed: {e}", exc_info=True)
            all_results['institutional_holdings'] = {}

        # 4. Collect SEC Form 4 Data (Insider Transactions)
        logger.info("\n" + "="*70)
        logger.info("STEP 4: Collecting SEC Form 4 Data (Insider Transactions)")
        logger.info("="*70)
        try:
            form4_collector = Form4Collector()
            form4_results = form4_collector.collect_all_tickers(start_date, end_date)
            all_results['insider_transactions'] = form4_results
            logger.info(f"Form 4 collection complete. Total records: {sum(form4_results.values())}")
        except Exception as e:
            logger.error(f"Form 4 collection failed: {e}", exc_info=True)
            all_results['insider_transactions'] = {}

        # 5. Run Data Validation
        logger.info("\n" + "="*70)
        logger.info("STEP 5: Running Data Validation")
        logger.info("="*70)
        try:
            validator = DataValidator()
            validation_report = validator.validate_all()
            validator.print_report(validation_report)
        except Exception as e:
            logger.error(f"Data validation failed: {e}", exc_info=True)

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("COLLECTION SUMMARY")
        logger.info("="*70)

        for data_type, results in all_results.items():
            total = sum(results.values()) if results else 0
            logger.info(f"{data_type}: {total} records")

        logger.info("\n" + "="*70)
        logger.info("Data collection complete!")
        logger.info("="*70)

        return 0

    except Exception as e:
        logger.error(f"Fatal error during data collection: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
