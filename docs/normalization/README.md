# Data Normalization Module

This module is responsible for converting raw data from different sources (Stock Prices, Google Trends, Institutional Holdings) into a standard Z-Score scale. This allows for direct comparison of disparate data types on the dashboard.

## Quick Start

The normalization logic is encapsulated in the `ZScoreNormalizer` class.

```python
from src.database.base import get_session
from src.processors.normalization import ZScoreNormalizer

with get_session() as session:
    normalizer = ZScoreNormalizer(session)
    
    # Process a single ticker
    records_processed = normalizer.process_ticker(ticker_id=1)
    
    print(f"Computed Z-Scores for {records_processed} days")
```

## Key Features

- **Multi-Source Alignment**: Merges Daily (Prices), Weekly (Trends), and Quarterly (Holdings) data.
- **Robust Statistics**: Uses a rolling 30-day window to calculate Mean and Standard Deviation.
- **Outlier Handling**: Automatically handles gaps and zero-variance periods.

## Optimization Notes
> [!NOTE]
> **Performance**: The current implementation uses standard SQLAlchemy ORM `add_all()` for persistence. 
> For the MVP dataset (12 tickers), this is sufficiently fast. 
> For high-frequency / large-scale data in Phase 3, consider refactoring `_save_scores` to use `bulk_insert_mappings()` to bypass ORM overhead.

## Usage Examples

### Single Ticker Processing

```python
from src.database.base import get_session
from src.processors.normalization import ZScoreNormalizer

with get_session() as session:
    normalizer = ZScoreNormalizer(session)
    count = normalizer.process_ticker(ticker_id=1)
    print(f"Calculated {count} scores")
```

### Batch Processing (Crawler Pattern)

```python
from src.database.models import Ticker

with get_session() as session:
    normalizer = ZScoreNormalizer(session)
    tickers = session.query(Ticker).all()
    
    for ticker in tickers:
        try:
            count = normalizer.process_ticker(ticker.ticker_id)
            print(f"Processed {ticker.symbol}: {count}")
        except Exception as e:
            print(f"Failed {ticker.symbol}: {e}")
```
