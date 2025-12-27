"""Script to verify mock data quality and coverage"""

from datetime import datetime

from sqlalchemy import func

from src.config import get_settings
from src.database import (
    GoogleTrend,
    InsiderTransaction,
    InstitutionalHolding,
    Price,
    RedditSentiment,
    Ticker,
    get_session,
)

settings = get_settings()


def verify_mock_data():
    """Verify that mock data was generated correctly"""

    print("\n" + "=" * 70)
    print("Mock Data Verification Report")
    print("=" * 70 + "\n")

    with get_session() as session:
        # Check tickers
        tickers = session.query(Ticker).all()
        print(f"[TICKERS] Tickers in Database: {len(tickers)}")
        print(f"   Expected: {len(settings.WHITELISTED_TICKERS)}")

        if len(tickers) != len(settings.WHITELISTED_TICKERS):
            print("   [WARN]  WARNING: Ticker count mismatch!")
        else:
            print("   [OK] All tickers present")

        print("\n" + "-" * 70 + "\n")

        # Check each ticker's data
        for ticker in tickers:
            symbol = ticker.symbol
            print(f"[DATA] {symbol} - {ticker.company_name}")

            # Price data
            price_count = (
                session.query(Price)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
            )
            if price_count > 0:
                first_date = (
                    session.query(func.min(Price.date))
                    .filter_by(ticker_id=ticker.ticker_id)
                    .scalar()
                )
                last_date = (
                    session.query(func.max(Price.date))
                    .filter_by(ticker_id=ticker.ticker_id)
                    .scalar()
                )
                print(f"   Price Data: {price_count} records ({first_date} to {last_date})")
            else:
                print(f"   Price Data: [ERROR] NO DATA")

            # Institutional holdings
            holdings_count = (
                session.query(InstitutionalHolding)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
            )
            if holdings_count > 0:
                print(f"   Institutional Holdings: {holdings_count} quarters")
            else:
                print(f"   Institutional Holdings: [ERROR] NO DATA")

            # Insider transactions
            insider_count = (
                session.query(InsiderTransaction)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
            )
            if insider_count > 0:
                print(f"   Insider Transactions: {insider_count} transactions")
            else:
                print(f"   Insider Transactions: [ERROR] NO DATA")

            # Google Trends
            trends_count = (
                session.query(GoogleTrend)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
            )
            if trends_count > 0:
                print(f"   Google Trends: {trends_count} weeks")
            else:
                print(f"   Google Trends: [ERROR] NO DATA")

            # Reddit sentiment
            reddit_count = (
                session.query(RedditSentiment)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
            )
            if reddit_count > 0:
                avg_mentions = (
                    session.query(func.avg(RedditSentiment.mention_count))
                    .filter_by(ticker_id=ticker.ticker_id)
                    .scalar()
                )
                avg_sentiment = (
                    session.query(func.avg(RedditSentiment.sentiment_score))
                    .filter_by(ticker_id=ticker.ticker_id)
                    .scalar()
                )
                print(
                    f"   Reddit Sentiment: {reddit_count} days "
                    f"(avg {avg_mentions:.0f} mentions, {avg_sentiment:+.2f} sentiment)"
                )
            else:
                print(f"   Reddit Sentiment: [ERROR] NO DATA")

            print()

        # Summary statistics
        print("-" * 70)
        print("\n[SUMMARY] Database Summary:")
        total_price_records = session.query(Price).count()
        total_holdings = session.query(InstitutionalHolding).count()
        total_insider = session.query(InsiderTransaction).count()
        total_trends = session.query(GoogleTrend).count()
        total_reddit = session.query(RedditSentiment).count()

        print(f"   Total Price Records: {total_price_records:,}")
        print(f"   Total Institutional Holdings: {total_holdings:,}")
        print(f"   Total Insider Transactions: {total_insider:,}")
        print(f"   Total Google Trends Records: {total_trends:,}")
        print(f"   Total Reddit Sentiment Records: {total_reddit:,}")

        total_records = (
            total_price_records
            + total_holdings
            + total_insider
            + total_trends
            + total_reddit
        )
        print(f"\n   [DATA] GRAND TOTAL: {total_records:,} records")

        # Check for data completeness
        print("\n" + "-" * 70)
        print("\n[CHECK] Data Quality Checks:")

        all_complete = True

        # Check if all tickers have all data types
        for ticker in tickers:
            symbol = ticker.symbol
            has_price = (
                session.query(Price)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
                > 0
            )
            has_holdings = (
                session.query(InstitutionalHolding)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
                > 0
            )
            has_insider = (
                session.query(InsiderTransaction)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
                > 0
            )
            has_trends = (
                session.query(GoogleTrend)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
                > 0
            )
            has_reddit = (
                session.query(RedditSentiment)
                .filter_by(ticker_id=ticker.ticker_id)
                .count()
                > 0
            )

            if not all([has_price, has_holdings, has_insider, has_trends, has_reddit]):
                print(f"   [WARN]  {symbol} is missing some data types")
                all_complete = False

        if all_complete:
            print("   [OK] All tickers have complete data across all types")
        else:
            print("   [WARN]  Some tickers are missing data")

        # Date range check
        min_date = session.query(func.min(Price.date)).scalar()
        max_date = session.query(func.max(Price.date)).scalar()

        if min_date and max_date:
            print(f"\n   Date Range: {min_date} to {max_date}")
            expected_start = settings.DATA_START_DATE.date()
            if min_date <= expected_start:
                print(f"   [OK] Start date matches expected ({expected_start})")
            else:
                print(f"   [WARN]  Start date later than expected ({expected_start})")

        print("\n" + "=" * 70)

        if all_complete and total_records > 0:
            print("[CHECK] VERIFICATION PASSED - Mock data is ready for dashboard testing!")
        else:
            print("[WARN]  VERIFICATION FAILED - Please regenerate mock data")

        print("=" * 70 + "\n")


if __name__ == "__main__":
    verify_mock_data()
