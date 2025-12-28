import sys
import os

# Add project root to path BEFORE imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from sqlalchemy import select, func
from src.database.base import get_session
from src.database.models import Ticker, Price, ZScore

def verify_data():
    with get_session() as session:
        # 1. Check Tickers
        tickers = session.execute(select(Ticker)).scalars().all()
        print(f"Total Tickers: {len(tickers)}")
        for t in tickers:
            print(f" - {t.symbol}: {t.company_name}")

        if not tickers:
            print("\nWARNING: No tickers found! Database is empty.")
            return

        # 2. Per-Ticker Summary
        print(f"\n{'TICKER':<8} | {'PRICE_Z':<8} | {'INST_Z':<8} | {'RETAIL_Z':<8} | {'STATUS':<15}")
        print("-" * 60)
        
        for t in tickers:
            p_z_count = session.execute(select(func.count(ZScore.z_score_id)).where(ZScore.ticker_id == t.ticker_id).where(ZScore.price_z.is_not(None))).scalar()
            i_z_count = session.execute(select(func.count(ZScore.z_score_id)).where(ZScore.ticker_id == t.ticker_id).where(ZScore.institutional_z.is_not(None))).scalar()
            r_z_count = session.execute(select(func.count(ZScore.z_score_id)).where(ZScore.ticker_id == t.ticker_id).where(ZScore.retail_search_z.is_not(None))).scalar()
            
            # Simple status check
            if i_z_count == 0:
                status = "MISSING INST"
            elif p_z_count == 0:
                 status = "MISSING PRICE"
            else:
                status = "OK"
                
            print(f"{t.symbol:<8} | {p_z_count:<8} | {i_z_count:<8} | {r_z_count:<8} | {status:<15}")

        print("\nNote: 'MISSING INST' means Smart Money Z-Scores are Null (likely due to insufficient quarterly data).")

        print("\nNote: 'PARTIAL' is expected due to rolling window startup periods (e.g. first 30 days).")

if __name__ == "__main__":
    verify_data()
