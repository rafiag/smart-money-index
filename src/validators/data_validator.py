"""Data quality validation and reporting"""

from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
from sqlalchemy import func

from src.config import get_settings
from src.database import (
    GoogleTrend,
    InsiderTransaction,
    InstitutionalHolding,
    Price,
    Ticker,
    get_session,
)
from src.utils import get_logger


class DataValidator:
    """
    Validates data quality and generates reports.

    Implements validation rules from TECHNICAL-SPEC.md:
    - Ticker symbol validation
    - Missing data detection
    - Outlier flagging
    - Data completeness checks
    - Type validation
    - Range checks
    """

    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.issues: List[Dict] = []

    def validate_all(self) -> Dict:
        """
        Run all validation checks and return report.

        Returns:
            Dictionary with validation results and issues
        """
        self.logger.info("Starting data validation...")
        self.issues = []

        # Run all validation checks
        self.validate_tickers()
        self.validate_price_data()
        self.validate_institutional_data()
        self.validate_insider_data()
        self.validate_google_trends()
        self.validate_completeness()

        # Generate report
        report = {
            "timestamp": datetime.now(),
            "total_issues": len(self.issues),
            "issues": self.issues,
            "summary": self._generate_summary()
        }

        self.logger.info(f"Validation complete. Found {len(self.issues)} issues.")
        return report

    def validate_tickers(self) -> None:
        """Validate ticker symbols against whitelist"""
        with get_session() as session:
            tickers = session.query(Ticker).all()

            for ticker in tickers:
                if ticker.symbol not in self.settings.WHITELISTED_TICKERS:
                    self.issues.append({
                        "severity": "ERROR",
                        "category": "TICKER_VALIDATION",
                        "message": f"Ticker {ticker.symbol} is not in whitelist",
                        "ticker": ticker.symbol
                    })

    def validate_price_data(self) -> None:
        """Validate price data for quality issues"""
        with get_session() as session:
            # Check each ticker
            for symbol in self.settings.WHITELISTED_TICKERS:
                ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()
                if not ticker:
                    continue

                # Get price data
                prices = session.query(Price).filter(
                    Price.ticker_id == ticker.ticker_id
                ).order_by(Price.date).all()

                if not prices:
                    self.issues.append({
                        "severity": "ERROR",
                        "category": "MISSING_DATA",
                        "message": f"No price data for {symbol}",
                        "ticker": symbol
                    })
                    continue

                # Check for gaps in data (weekdays only)
                dates = [p.date for p in prices]
                date_range = pd.date_range(
                    start=min(dates),
                    end=max(dates),
                    freq='B'  # Business days only
                )

                missing_dates = set(date_range.date) - set(dates)
                if missing_dates:
                    self.issues.append({
                        "severity": "WARNING",
                        "category": "DATA_GAPS",
                        "message": f"{symbol} missing {len(missing_dates)} trading days",
                        "ticker": symbol,
                        "count": len(missing_dates)
                    })

                # Check for invalid prices (must be > 0)
                for price in prices:
                    if price.close and price.close <= 0:
                        self.issues.append({
                            "severity": "ERROR",
                            "category": "INVALID_VALUE",
                            "message": f"{symbol} has invalid close price on {price.date}",
                            "ticker": symbol,
                            "date": price.date,
                            "value": float(price.close)
                        })

                    if price.volume and price.volume < 0:
                        self.issues.append({
                            "severity": "ERROR",
                            "category": "INVALID_VALUE",
                            "message": f"{symbol} has negative volume on {price.date}",
                            "ticker": symbol,
                            "date": price.date,
                            "value": price.volume
                        })

                # Check for outliers using IQR method
                close_prices = [float(p.close) for p in prices if p.close]
                if len(close_prices) > 10:
                    df = pd.DataFrame({'close': close_prices})
                    Q1 = df['close'].quantile(0.25)
                    Q3 = df['close'].quantile(0.75)
                    IQR = Q3 - Q1

                    lower_bound = Q1 - self.settings.IQR_MULTIPLIER * IQR
                    upper_bound = Q3 + self.settings.IQR_MULTIPLIER * IQR

                    outlier_count = 0
                    for price in prices:
                        if price.close:
                            if float(price.close) < lower_bound or float(price.close) > upper_bound:
                                outlier_count += 1

                    if outlier_count > 0:
                        self.issues.append({
                            "severity": "INFO",
                            "category": "OUTLIERS",
                            "message": f"{symbol} has {outlier_count} price outliers",
                            "ticker": symbol,
                            "count": outlier_count
                        })

    def validate_institutional_data(self) -> None:
        """Validate institutional holdings data"""
        with get_session() as session:
            for symbol in self.settings.WHITELISTED_TICKERS:
                ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()
                if not ticker:
                    continue

                holdings = session.query(InstitutionalHolding).filter(
                    InstitutionalHolding.ticker_id == ticker.ticker_id
                ).all()

                if not holdings:
                    self.issues.append({
                        "severity": "WARNING",
                        "category": "MISSING_DATA",
                        "message": f"No institutional holdings data for {symbol}",
                        "ticker": symbol
                    })
                    continue

                # Check for valid percentage range
                for holding in holdings:
                    if holding.ownership_percent:
                        if not (0 <= float(holding.ownership_percent) <= 100):
                            self.issues.append({
                                "severity": "ERROR",
                                "category": "INVALID_VALUE",
                                "message": f"{symbol} has invalid ownership percent",
                                "ticker": symbol,
                                "date": holding.quarter_end,
                                "value": float(holding.ownership_percent)
                            })

    def validate_insider_data(self) -> None:
        """Validate insider transaction data"""
        with get_session() as session:
            for symbol in self.settings.WHITELISTED_TICKERS:
                ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()
                if not ticker:
                    continue

                transactions = session.query(InsiderTransaction).filter(
                    InsiderTransaction.ticker_id == ticker.ticker_id
                ).all()

                # Insider data is optional, just log if missing
                if not transactions:
                    self.logger.debug(f"No insider transaction data for {symbol}")

                # Validate transaction types
                for trans in transactions:
                    if trans.transaction_type not in ['buy', 'sell']:
                        self.issues.append({
                            "severity": "ERROR",
                            "category": "INVALID_VALUE",
                            "message": f"{symbol} has invalid transaction type",
                            "ticker": symbol,
                            "date": trans.transaction_date,
                            "value": trans.transaction_type
                        })

    def validate_google_trends(self) -> None:
        """Validate Google Trends data"""
        with get_session() as session:
            for symbol in self.settings.WHITELISTED_TICKERS:
                ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()
                if not ticker:
                    continue

                trends = session.query(GoogleTrend).filter(
                    GoogleTrend.ticker_id == ticker.ticker_id
                ).all()

                if not trends:
                    self.issues.append({
                        "severity": "WARNING",
                        "category": "MISSING_DATA",
                        "message": f"No Google Trends data for {symbol}",
                        "ticker": symbol
                    })
                    continue

                # Validate search interest is in 0-100 range
                for trend in trends:
                    if trend.search_interest is not None:
                        if not (0 <= trend.search_interest <= 100):
                            self.issues.append({
                                "severity": "ERROR",
                                "category": "INVALID_VALUE",
                                "message": f"{symbol} has invalid search interest",
                                "ticker": symbol,
                                "date": trend.date,
                                "value": trend.search_interest
                            })


    def validate_completeness(self) -> None:
        """Check that all tickers have data for expected date ranges"""
        with get_session() as session:
            start_date = self.settings.DATA_START_DATE.date()
            end_date = datetime.now().date()

            for symbol in self.settings.WHITELISTED_TICKERS:
                ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()
                if not ticker:
                    self.issues.append({
                        "severity": "ERROR",
                        "category": "MISSING_TICKER",
                        "message": f"Ticker {symbol} not found in database",
                        "ticker": symbol
                    })
                    continue

                # Check price data coverage
                price_count = session.query(func.count(Price.price_id)).filter(
                    Price.ticker_id == ticker.ticker_id,
                    Price.date >= start_date,
                    Price.date <= end_date
                ).scalar()

                # Calculate expected trading days
                expected_days = len(pd.date_range(start=start_date, end=end_date, freq='B'))

                if price_count < expected_days * 0.95:  # Allow 5% missing
                    self.issues.append({
                        "severity": "WARNING",
                        "category": "INCOMPLETE_DATA",
                        "message": f"{symbol} price data is {int(price_count/expected_days*100)}% complete",
                        "ticker": symbol,
                        "expected": expected_days,
                        "actual": price_count
                    })

    def _generate_summary(self) -> Dict:
        """Generate summary statistics for validation report"""
        summary = {
            "total_issues": len(self.issues),
            "by_severity": {},
            "by_category": {},
            "by_ticker": {}
        }

        for issue in self.issues:
            # Count by severity
            severity = issue.get("severity", "UNKNOWN")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1

            # Count by category
            category = issue.get("category", "UNKNOWN")
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1

            # Count by ticker
            ticker = issue.get("ticker", "UNKNOWN")
            summary["by_ticker"][ticker] = summary["by_ticker"].get(ticker, 0) + 1

        return summary

    def print_report(self, report: Dict) -> None:
        """Print validation report to console"""
        print("\n" + "="*70)
        print("DATA VALIDATION REPORT")
        print("="*70)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total Issues: {report['total_issues']}")
        print()

        summary = report['summary']

        print("By Severity:")
        for severity, count in sorted(summary['by_severity'].items()):
            print(f"  {severity}: {count}")
        print()

        print("By Category:")
        for category, count in sorted(summary['by_category'].items()):
            print(f"  {category}: {count}")
        print()

        print("By Ticker:")
        for ticker, count in sorted(summary['by_ticker'].items()):
            print(f"  {ticker}: {count}")
        print()

        if report['issues']:
            print("Issues (showing first 20):")
            for issue in report['issues'][:20]:
                print(f"  [{issue['severity']}] {issue['message']}")

        print("="*70)
