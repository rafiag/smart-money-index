"""Google Trends data collector"""

import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from pytrends.request import TrendReq
from sqlalchemy.exc import IntegrityError

from src.database import GoogleTrend, get_session
from src.utils import get_logger

from .base import BaseCollector


class GoogleTrendsCollector(BaseCollector):
    """Collects search interest data from Google Trends"""

    def __init__(self):
        """Initialize Google Trends collector with rate limit"""
        super().__init__(rate_limit=100)  # ~100 requests per hour
        self.logger = get_logger(__name__)

        # Initialize pytrends
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10, 25),
            retries=3,
            backoff_factor=0.5
        )

    def collect_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Collect Google Trends search interest data.

        Note: Google Trends returns weekly data for date ranges > 90 days.
        We'll interpolate to daily for consistency.

        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date (defaults to today)

        Returns:
            Number of records inserted
        """
        if end_date is None:
            end_date = datetime.now()

        self.logger.info(
            f"Fetching Google Trends data for {symbol} from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Use rate limiter
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed()

            # Build timeframe string for Google Trends
            timeframe = f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"

            # Build payload - search for ticker symbol
            kw_list = [symbol]

            self.pytrends.build_payload(
                kw_list,
                timeframe=timeframe,
                geo='US',  # United States only
                gprop=''  # Web search
            )

            # Get interest over time
            df = self.pytrends.interest_over_time()

            if df.empty:
                self.logger.warning(f"No Google Trends data found for {symbol}")
                return 0

            # Drop 'isPartial' column if present
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])

            # Get the data for our symbol
            if symbol not in df.columns:
                self.logger.warning(f"Symbol {symbol} not in Google Trends response")
                return 0

            # If data is weekly, interpolate to daily
            df = df[[symbol]].copy()
            df.index = pd.to_datetime(df.index)

            # Resample to daily using linear interpolation
            df_daily = df.resample('D').interpolate(method='linear')

            # Fill forward for the last few days if needed
            df_daily = df_daily.fillna(method='ffill')
            df_daily = df_daily.fillna(0)  # Fill any remaining NaN with 0

            # Insert into database
            records_inserted = 0

            with get_session() as session:
                ticker_obj = self.get_or_create_ticker(session, symbol)

                for date_idx, row in df_daily.iterrows():
                    try:
                        trend = GoogleTrend(
                            ticker_id=ticker_obj.ticker_id,
                            date=date_idx.date(),
                            search_interest=int(round(row[symbol]))
                        )
                        session.add(trend)
                        records_inserted += 1

                    except IntegrityError:
                        session.rollback()
                        self.logger.debug(
                            f"Google Trends record for {symbol} on {date_idx.date()} already exists"
                        )
                    except Exception as e:
                        session.rollback()
                        self.logger.error(
                            f"Error inserting trend record for {symbol} on {date_idx.date()}: {e}"
                        )

                session.commit()

            self.logger.info(
                f"Inserted {records_inserted} Google Trends records for {symbol}"
            )

            # Add delay to be respectful to Google Trends
            time.sleep(2)

            return records_inserted

        except Exception as e:
            self.logger.error(
                f"Failed to collect Google Trends data for {symbol}: {e}",
                exc_info=True
            )

            # If we hit rate limit, wait longer
            if '429' in str(e) or 'quota' in str(e).lower():
                self.logger.warning("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)

            return 0
