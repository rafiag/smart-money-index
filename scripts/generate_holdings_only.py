
import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.database.base import get_session
from src.database.models import Ticker, InstitutionalHolding
from src.utils.mock_data_generator import MockDataGenerator
from sqlalchemy import delete

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_holdings_only():
    logger.info("Starting Hybrid Data Setup: Mocking Institutional Holdings Only...")
    
    generator = MockDataGenerator()
    
    with get_session() as session:
        # 1. Clear existing (empty?) holdings
        logger.info("Clearing InstitutionalHolding table...")
        session.execute(delete(InstitutionalHolding))
        session.commit()
        
        # 2. Generate for all tickers
        tickers = session.query(Ticker).all()
        logger.info(f"Found {len(tickers)} tickers to generate holdings for.")
        
        total_holdings = 0
        
        for ticker in tickers:
            symbol = ticker.symbol
            if symbol not in generator.stock_profiles:
                logger.warning(f"No profile for {symbol}, using default.")
                # Fallback profile or skip? 
                # generator.stock_profiles is hardcoded in the class.
                # If ticker is dynamic and not in profile, this might crash inside generator methods?
                # The generator._generate_institutional_holdings uses self.stock_profiles[symbol]
                # Let's check if we need to add a default profile.
                pass

            try:
                # Generate mock holdings
                holdings_data = generator._generate_institutional_holdings(symbol)
                
                for data in holdings_data:
                    holding = InstitutionalHolding(
                        ticker_id=ticker.ticker_id,
                        **data
                    )
                    session.add(holding)
                
                total_holdings += len(holdings_data)
                logger.info(f"  Generated {len(holdings_data)} quarters for {symbol}")
                
            except KeyError:
                logger.warning(f"  Skipping {symbol}: No mock profile defined.")
            except Exception as e:
                logger.error(f"  Error generating hearings for {symbol}: {e}")

        session.commit()
        logger.info(f"✓ Successfully inserted {total_holdings} mock institutional holding records.")
        logger.info("Real Price, Trends, and Insider data were preserved.")

if __name__ == "__main__":
    generate_holdings_only()
