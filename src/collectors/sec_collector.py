"""SEC data collectors for Form 13F and Form 4"""

import time
from datetime import datetime, timedelta
from typing import Optional

from edgar import Company, set_identity
from sqlalchemy.exc import IntegrityError

from src.database import InsiderTransaction, InstitutionalHolding, get_session
from src.utils import get_logger

from .base import BaseCollector


def retry_on_network_error(max_retries=3, initial_delay=2):
    """
    Decorator to retry a function on network/SSL errors with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (doubles with each retry)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OSError, TimeoutError, ConnectionError, Exception) as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Check if it's a network-related error
                    is_network_error = any(keyword in error_msg for keyword in [
                        'ssl', 'timeout', 'connection', 'socket', 'network',
                        'read', 'recv', 'stream', 'http'
                    ])
                    
                    # Also check exception type
                    is_network_error = is_network_error or isinstance(e, (
                        OSError, TimeoutError, ConnectionError
                    ))
                    
                    if not is_network_error or attempt == max_retries:
                        # Not a network error or max retries reached
                        raise
                    
                    # Log and retry
                    logger = get_logger(__name__)
                    logger.warning(
                        f"Network error on attempt {attempt + 1}/{max_retries + 1}: {e}. "
                        f"Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class Form13FCollector(BaseCollector):
    """Collects institutional holdings from SEC Form 13F filings"""

    def __init__(self):
        """Initialize 13F collector with SEC rate limit"""
        super().__init__(rate_limit=30)  # SEC: More conservative - 1 request per 2 seconds
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

            # Check if filings were found
            if filings_13f is None or not filings_13f:
                self.logger.warning(f"No 13F filings found for {symbol}")
                return 0

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
                            # Use retry decorator for network resilience
                            @retry_on_network_error(max_retries=3, initial_delay=2)
                            def fetch_filing_data():
                                return filing.obj()
                            
                            holdings_data = fetch_filing_data()  # Get filing object

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
        super().__init__(rate_limit=30)  # SEC: More conservative - 1 request per 2 seconds
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

            # Check if filings were found
            if filings_form4 is None or not filings_form4:
                self.logger.warning(f"No Form 4 filings found for {symbol}")
                return 0

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

                        # Parse Form 4 XML data
                        try:
                            # Use retry decorator for network resilience
                            @retry_on_network_error(max_retries=3, initial_delay=2)
                            def fetch_filing_xml():
                                return filing.xml()
                            
                            xml_content = fetch_filing_xml()
                            
                            if not xml_content:
                                self.logger.warning(f"No XML content for Form 4 filing on {filing_date}")
                                continue
                            
                            # Parse XML
                            import xml.etree.ElementTree as ET
                            root = ET.fromstring(xml_content)
                            
                            # Extract transactions from nonDerivativeTable
                            transactions_found = 0
                            for transaction in root.findall('.//nonDerivativeTransaction'):
                                # Extract transaction date
                                trans_date_elem = transaction.find('.//transactionDate/value')
                                if trans_date_elem is None or not trans_date_elem.text:
                                    continue
                                
                                try:
                                    transaction_date = datetime.strptime(trans_date_elem.text, '%Y-%m-%d').date()
                                except ValueError:
                                    self.logger.warning(f"Invalid transaction date format: {trans_date_elem.text}")
                                    continue
                                
                                # Extract shares
                                shares_elem = transaction.find('.//transactionShares/value')
                                if shares_elem is None or not shares_elem.text:
                                    continue
                                
                                try:
                                    shares_traded = abs(int(float(shares_elem.text)))
                                except (ValueError, TypeError):
                                    self.logger.warning(f"Invalid shares value: {shares_elem.text}")
                                    continue
                                
                                if shares_traded == 0:
                                    continue
                                
                                # Extract transaction code
                                code_elem = transaction.find('.//transactionCode')
                                transaction_code = code_elem.text if code_elem is not None and code_elem.text else 'P'
                                
                                # Extract acquired/disposed code
                                acquired_disposed_elem = transaction.find('.//transactionAcquiredDisposedCode/value')
                                acquired_disposed = acquired_disposed_elem.text if acquired_disposed_elem is not None and acquired_disposed_elem.text else 'A'
                                
                                # Determine buy/sell based on transaction code
                                # Buy codes: P (Purchase), A (Award/Grant), M (Exercise)
                                # Sell codes: S (Sale), D (Disposition), F (Tax payment), G (Gift)
                                if transaction_code in ['P', 'A', 'M']:
                                    transaction_type = 'buy'
                                elif transaction_code in ['S', 'D', 'F', 'G']:
                                    transaction_type = 'sell'
                                else:
                                    # Use acquired/disposed as fallback
                                    transaction_type = 'buy' if acquired_disposed == 'A' else 'sell'
                                
                                # Create transaction record
                                transaction_record = InsiderTransaction(
                                    ticker_id=ticker_obj.ticker_id,
                                    transaction_date=transaction_date,
                                    shares_traded=shares_traded,
                                    transaction_type=transaction_type
                                )
                                session.add(transaction_record)
                                session.flush()
                                records_inserted += 1
                                transactions_found += 1
                            
                            if transactions_found == 0:
                                self.logger.debug(f"No transactions found in Form 4 for {symbol} on {filing_date}")

                        except ET.ParseError as xml_error:
                            self.logger.warning(
                                f"Could not parse Form 4 XML for {symbol} on {filing_date}: {xml_error}"
                            )
                            continue
                        except Exception as parse_error:
                            self.logger.warning(
                                f"Could not extract Form 4 data for {symbol} on {filing_date}: {parse_error}"
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
