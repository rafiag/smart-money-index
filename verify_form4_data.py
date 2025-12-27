"""Verify Form 4 data in database"""
from src.database import get_session
from src.database.models import InsiderTransaction, Ticker

with get_session() as session:
    results = session.query(InsiderTransaction, Ticker).join(Ticker).filter(
        Ticker.symbol == 'AAPL'
    ).order_by(InsiderTransaction.transaction_date.desc()).limit(10).all()

    print('Recent AAPL Insider Transactions:')
    print('=' * 70)
    for it, t in results:
        print(f'{it.transaction_date} | {it.transaction_type:4s} | {it.shares_traded:>10,} shares')

    print('=' * 70)
    print(f'Total records found: {len(results)}')

