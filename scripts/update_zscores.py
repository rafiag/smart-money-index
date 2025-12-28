import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from sqlalchemy import select
from src.database.base import get_session
from src.database.models import Ticker
from src.processors.normalization import ZScoreNormalizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_all_zscores():
    logger.info("Starting Z-Score Update Pipeline...")
    
    with get_session() as session:
        # 1. Get all tickers
        tickers = session.execute(select(Ticker)).scalars().all()
        logger.info(f"Found {len(tickers)} tickers to process.")
        
        normalizer = ZScoreNormalizer(session)
        total_records = 0
        
        for ticker in tickers:
            try:
                logger.info(f"Processing {ticker.symbol}...")
                records = normalizer.process_ticker(ticker.ticker_id)
                total_records += records
                logger.info(f"  Saved {records} Z-score records for {ticker.symbol}")
            except Exception as e:
                logger.error(f"  Error processing {ticker.symbol}: {e}")
                session.rollback()
        
        logger.info(f"Pipeline Complete. Total Z-Score records saved: {total_records}")

if __name__ == "__main__":
    update_all_zscores()
