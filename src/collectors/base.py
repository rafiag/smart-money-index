"""Base collector class with common functionality"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.config import get_settings
from src.database import Ticker, get_session
from src.utils import RateLimiter, get_logger


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.

    Provides common functionality:
    - Rate limiting
    - Database session management
    - Ticker validation
    - Logging
    - Template methods for historical and incremental collection
    """

    def __init__(self, rate_limit: Optional[int] = None):
        """
        Initialize collector.

        Args:
            rate_limit: Requests per minute limit (uses config default if not provided)
        """
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)

        # Rate limiter (subclasses should override with specific limits)
        if rate_limit:
            self.rate_limiter = RateLimiter(max_calls=rate_limit, period=60)
        else:
            self.rate_limiter = None

    def get_or_create_ticker(self, session: Session, symbol: str) -> Ticker:
        """
        Get existing ticker or create new one.

        Args:
            session: Database session
            symbol: Ticker symbol (e.g., 'AAPL')

        Returns:
            Ticker object

        Raises:
            ValueError: If ticker is not in whitelist
        """
        # Validate ticker is whitelisted
        if symbol not in self.settings.WHITELISTED_TICKERS:
            raise ValueError(
                f"Ticker {symbol} is not in whitelist. "
                f"Allowed tickers: {', '.join(self.settings.WHITELISTED_TICKERS)}"
            )

        # Try to get existing ticker
        ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()

        if ticker is None:
            # Create new ticker
            company_name = self.settings.TICKER_COMPANY_MAP.get(
                symbol, f"{symbol} Inc."
            )
            ticker = Ticker(symbol=symbol, company_name=company_name)
            session.add(ticker)
            session.flush()  # Get the ticker_id without committing
            self.logger.info(f"Created new ticker: {symbol} ({company_name})")

        return ticker

    def get_all_tickers(self, session: Session) -> List[Ticker]:
        """
        Get all whitelisted tickers from database, creating them if needed.

        Args:
            session: Database session

        Returns:
            List of Ticker objects
        """
        tickers = []
        for symbol in self.settings.WHITELISTED_TICKERS:
            ticker = self.get_or_create_ticker(session, symbol)
            tickers.append(ticker)
        return tickers

    @abstractmethod
    def collect_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Collect historical data for a ticker.

        Args:
            symbol: Ticker symbol
            start_date: Start date for data collection
            end_date: End date (defaults to today)

        Returns:
            Number of records collected
        """
        pass

    def collect_incremental(
        self,
        symbol: str,
        since_date: datetime
    ) -> int:
        """
        Collect incremental data since last update (Phase 2).

        Default implementation calls collect_historical.
        Override in subclasses for optimized incremental collection.

        Args:
            symbol: Ticker symbol
            since_date: Date to collect data from

        Returns:
            Number of records collected
        """
        self.logger.info(
            f"Incremental collection not yet optimized for {self.__class__.__name__}. "
            f"Falling back to historical collection."
        )
        return self.collect_historical(symbol, since_date)

    def collect_all_tickers(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Collect data for all whitelisted tickers.

        Args:
            start_date: Start date (defaults to DATA_START_DATE from config)
            end_date: End date (defaults to today)

        Returns:
            Dictionary with ticker symbols as keys and record counts as values
        """
        if start_date is None:
            start_date = self.settings.DATA_START_DATE

        if end_date is None:
            end_date = datetime.now()

        results = {}

        for symbol in self.settings.WHITELISTED_TICKERS:
            try:
                self.logger.info(
                    f"Collecting {self.__class__.__name__} data for {symbol}"
                )
                count = self.collect_historical(symbol, start_date, end_date)
                results[symbol] = count
                self.logger.info(f"Collected {count} records for {symbol}")

            except Exception as e:
                self.logger.error(
                    f"Failed to collect data for {symbol}: {str(e)}",
                    exc_info=True
                )
                results[symbol] = 0

        return results
