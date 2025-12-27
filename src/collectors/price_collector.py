"""Price data collector using Yahoo Finance API"""

from datetime import datetime
from typing import Optional

import yfinance as yf
from sqlalchemy.exc import IntegrityError

from src.database import Price, get_session
from src.utils import get_logger

from .base import BaseCollector


class PriceCollector(BaseCollector):
    """Collects daily OHLCV price data from Yahoo Finance"""

    def __init__(self):
        """Initialize price collector with Yahoo Finance rate limit"""
        super().__init__(rate_limit=2000)  # Yahoo Finance is generous
        self.logger = get_logger(__name__)

    def collect_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Collect historical price data for a ticker.

        Args:
            symbol: Ticker symbol (e.g., 'AAPL')
            start_date: Start date for data collection
            end_date: End date (defaults to today)

        Returns:
            Number of price records inserted
        """
        if end_date is None:
            end_date = datetime.now()

        self.logger.info(
            f"Fetching price data for {symbol} from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Use rate limiter if configured
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed()

            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval="1d"
            )

            if df.empty:
                self.logger.warning(f"No price data found for {symbol}")
                return 0

            # Insert into database
            records_inserted = 0

            with get_session() as session:
                # Get or create ticker
                ticker_obj = self.get_or_create_ticker(session, symbol)

                # Insert price records
                for date_idx, row in df.iterrows():
                    try:
                        price = Price(
                            ticker_id=ticker_obj.ticker_id,
                            date=date_idx.date(),
                            open=round(float(row['Open']), 2),
                            high=round(float(row['High']), 2),
                            low=round(float(row['Low']), 2),
                            close=round(float(row['Close']), 2),
                            volume=int(row['Volume']) if row['Volume'] else None
                        )
                        session.add(price)
                        records_inserted += 1

                    except IntegrityError:
                        # Record already exists (duplicate date)
                        session.rollback()
                        self.logger.debug(
                            f"Price record for {symbol} on {date_idx.date()} already exists"
                        )
                    except Exception as e:
                        session.rollback()
                        self.logger.error(
                            f"Error inserting price record for {symbol} on {date_idx.date()}: {e}"
                        )

                session.commit()

            self.logger.info(
                f"Inserted {records_inserted} price records for {symbol}"
            )
            return records_inserted

        except Exception as e:
            self.logger.error(
                f"Failed to collect price data for {symbol}: {e}",
                exc_info=True
            )
            return 0
