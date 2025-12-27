"""SEC data collectors for Form 13F and Form 4"""

from datetime import datetime, timedelta
from typing import Optional

from edgar import Company, set_identity
from sqlalchemy.exc import IntegrityError

from src.database import InsiderTransaction, InstitutionalHolding, get_session
from src.utils import get_logger

from .base import BaseCollector


class Form13FCollector(BaseCollector):
    """Collects institutional holdings from SEC Form 13F filings"""

    def __init__(self):
        """Initialize 13F collector with SEC rate limit"""
        super().__init__(rate_limit=60)  # SEC: 1 request per second
        self.logger = get_logger(__name__)

        # Set identity for SEC EDGAR API (required)
        set_identity("Smart Money Divergence Index research@example.com")

    def collect_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Collect 13F institutional holdings data.

        Note: 13F data is quarterly with 45-day filing lag.

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
            f"Fetching 13F data for {symbol} from {start_date.date()} to {end_date.date()}"
        )

        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed()

            # Get company filings
            company = Company(symbol)
            filings_13f = company.get_filings(form="13F-HR").latest(20)

            records_inserted = 0

            with get_session() as session:
                ticker_obj = self.get_or_create_ticker(session, symbol)

                for filing in filings_13f:
                    try:
                        filing_date = filing.filing_date

                        # Skip if outside date range
                        if filing_date < start_date.date() or filing_date > end_date.date():
                            continue

                        if self.rate_limiter:
                            self.rate_limiter.wait_if_needed()

                        # Extract holdings data
                        # Note: This is simplified - real implementation would parse XML
                        # For MVP, we'll use aggregated data from the filing
                        quarter_end = filing.period_of_report

                        # Parse holdings from filing (simplified)
                        try:
                            holdings_data = filing.obj()  # Get filing object

                            # Extract total shares and value
                            # This is a simplified approach - production would parse XML properly
                            shares_held = 0
                            market_value = 0.0

                            # Try to get summary data
                            if hasattr(holdings_data, 'holdings'):
                                for holding in holdings_data.holdings:
                                    if holding.get('ticker', '').upper() == symbol:
                                        shares_held = int(holding.get('shares', 0))
                                        market_value = float(holding.get('value', 0))
                                        break

                            holding = InstitutionalHolding(
                                ticker_id=ticker_obj.ticker_id,
                                filing_date=filing_date,
                                quarter_end=quarter_end,
                                shares_held=shares_held if shares_held > 0 else None,
                                market_value=market_value if market_value > 0 else None,
                                ownership_percent=None  # Calculate later if needed
                            )
                            session.add(holding)
                            session.flush()
                            records_inserted += 1

                        except Exception as parse_error:
                            self.logger.warning(
                                f"Could not parse 13F filing for {symbol} on {filing_date}: {parse_error}"
                            )
                            continue

                    except IntegrityError:
                        session.rollback()
                        self.logger.debug(
                            f"13F record for {symbol} quarter {quarter_end} already exists"
                        )
                    except Exception as e:
                        session.rollback()
                        self.logger.error(
                            f"Error processing 13F filing for {symbol}: {e}"
                        )

                session.commit()

            self.logger.info(
                f"Inserted {records_inserted} 13F records for {symbol}"
            )
            return records_inserted

        except Exception as e:
            self.logger.error(
                f"Failed to collect 13F data for {symbol}: {e}",
                exc_info=True
            )
            return 0


class Form4Collector(BaseCollector):
    """Collects insider transactions from SEC Form 4 filings"""

    def __init__(self):
        """Initialize Form 4 collector with SEC rate limit"""
        super().__init__(rate_limit=60)  # SEC: 1 request per second
        self.logger = get_logger(__name__)

        # Set identity for SEC EDGAR API
        set_identity("Smart Money Divergence Index research@example.com")

    def collect_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Collect Form 4 insider transaction data.

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
            f"Fetching Form 4 data for {symbol} from {start_date.date()} to {end_date.date()}"
        )

        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed()

            # Get company filings
            company = Company(symbol)
            filings_form4 = company.get_filings(form="4").latest(100)

            records_inserted = 0

            with get_session() as session:
                ticker_obj = self.get_or_create_ticker(session, symbol)

                for filing in filings_form4:
                    try:
                        filing_date = filing.filing_date

                        # Skip if outside date range
                        if filing_date < start_date.date() or filing_date > end_date.date():
                            continue

                        if self.rate_limiter:
                            self.rate_limiter.wait_if_needed()

                        # Parse Form 4 data (simplified)
                        try:
                            form4_data = filing.obj()

                            # Extract transaction details
                            # This is simplified - production would parse XML properly
                            transaction_date = filing_date
                            shares_traded = 0
                            transaction_type = "buy"  # Default

                            # Try to extract transaction info
                            if hasattr(form4_data, 'transactions'):
                                for trans in form4_data.transactions:
                                    if trans.get('ticker', '').upper() == symbol:
                                        shares_traded = abs(int(trans.get('shares', 0)))
                                        # Determine buy/sell from transaction code
                                        code = trans.get('code', 'P')
                                        transaction_type = 'buy' if code in ['P', 'A'] else 'sell'
                                        transaction_date = trans.get('date', filing_date)
                                        break

                            if shares_traded > 0:
                                transaction = InsiderTransaction(
                                    ticker_id=ticker_obj.ticker_id,
                                    transaction_date=transaction_date,
                                    shares_traded=shares_traded,
                                    transaction_type=transaction_type
                                )
                                session.add(transaction)
                                session.flush()
                                records_inserted += 1

                        except Exception as parse_error:
                            self.logger.warning(
                                f"Could not parse Form 4 filing for {symbol} on {filing_date}: {parse_error}"
                            )
                            continue

                    except IntegrityError:
                        session.rollback()
                        self.logger.debug(
                            f"Form 4 record for {symbol} on {filing_date} already exists"
                        )
                    except Exception as e:
                        session.rollback()
                        self.logger.error(
                            f"Error processing Form 4 filing for {symbol}: {e}"
                        )

                session.commit()

            self.logger.info(
                f"Inserted {records_inserted} Form 4 records for {symbol}"
            )
            return records_inserted

        except Exception as e:
            self.logger.error(
                f"Failed to collect Form 4 data for {symbol}: {e}",
                exc_info=True
            )
            return 0
