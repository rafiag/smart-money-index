# Data Collection - Technical Reference

Complete technical documentation for the Phase 1.1 data collection system.

---

## Table of Contents

1. [API Reference](#api-reference)
2. [Collectors](#collectors)
3. [Database Models](#database-models)
4. [Data Validation](#data-validation)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [Rate Limiting](#rate-limiting)
8. [Error Handling](#error-handling)

---

## API Reference

### BaseCollector

**Location:** `src/collectors/base.py`

Abstract base class providing common functionality for all data collectors.

#### Constructor
```python
__init__(rate_limit: Optional[int] = None)
```
- `rate_limit` - Requests per minute (optional)

#### Methods

**collect_historical()**
```python
def collect_historical(
    symbol: str,
    start_date: datetime,
    end_date: Optional[datetime] = None
) -> int
```
Collect historical data for a ticker.

**Parameters:**
- `symbol` - Ticker symbol (must be whitelisted)
- `start_date` - Start date
- `end_date` - End date (defaults to today)

**Returns:** Number of records inserted

**Raises:** `ValueError` if ticker not whitelisted

**collect_incremental()** _(Phase 2)_
```python
def collect_incremental(symbol: str, since_date: datetime) -> int
```
Collect data since last update (currently calls `collect_historical`).

**collect_all_tickers()**
```python
def collect_all_tickers(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict
```
Collect data for all 12 whitelisted tickers.

**Returns:** `{'AAPL': 499, 'MSFT': 498, ...}`

**get_or_create_ticker()**
```python
def get_or_create_ticker(session: Session, symbol: str) -> Ticker
```
Get existing ticker or create new one.

---

## Collectors

### PriceCollector

**Location:** `src/collectors/price_collector.py`

Collects daily OHLCV price data from Yahoo Finance.

**Usage:**
```python
from src.collectors import PriceCollector
from datetime import datetime

collector = PriceCollector()
count = collector.collect_historical("AAPL", datetime(2024, 1, 1))
print(f"Collected {count} price records")
```

**Data Collected:**
- Open, High, Low, Close prices
- Volume
- Daily frequency

**Rate Limit:** 2000 req/min (very generous)

**Library:** `yfinance`

---

### GoogleTrendsCollector

**Location:** `src/collectors/google_trends_collector.py`

Collects search interest data from Google Trends.

**Usage:**
```python
from src.collectors import GoogleTrendsCollector
from datetime import datetime

collector = GoogleTrendsCollector()
count = collector.collect_historical("AAPL", datetime(2024, 1, 1))
```

**Data Collected:**
- Search interest (0-100 scale)
- Weekly data interpolated to daily using linear interpolation
- US region only

**Rate Limit:** ~100 req/hour (unofficial)

**Notes:**
- Automatic 2-second delay between requests
- Exponential backoff on rate limit errors
- Handles partial data gracefully

**Library:** `pytrends`

---

### RedditCollector

**Location:** `src/collectors/reddit_collector.py`

Collects sentiment data from Reddit.

**Usage:**
```python
from src.collectors import RedditCollector
from datetime import datetime

collector = RedditCollector()
count = collector.collect_historical("AAPL", datetime(2024, 1, 1))
```

**Data Collected:**
- Daily mention count
- Average sentiment score (-1 to +1)
- Subreddits: r/wallstreetbets, r/stocks, r/investing

**Authentication:** Requires Reddit API credentials in `.env`:
```
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
```

**Rate Limit:** 60 req/min (OAuth)

**Methods:**

**extract_tickers()**
```python
def extract_tickers(text: str) -> Set[str]
```
Extract ticker symbols from text. Matches `$AAPL` or `AAPL`.

**analyze_sentiment()**
```python
def analyze_sentiment(text: str) -> float
```
Analyze sentiment using TextBlob. Returns polarity (-1 to +1).

**Library:** `praw`, `textblob`

---

### Form13FCollector

**Location:** `src/collectors/sec_collector.py`

Collects institutional holdings from SEC Form 13F filings.

**Usage:**
```python
from src.collectors import Form13FCollector
from datetime import datetime

collector = Form13FCollector()
count = collector.collect_historical("AAPL", datetime(2024, 1, 1))
```

**Data Collected:**
- Filing date
- Quarter end date
- Shares held
- Market value
- Ownership percentage

**Frequency:** Quarterly (45-day filing lag)

**Rate Limit:** 60 req/min (SEC EDGAR)

**Library:** `edgartools`

---

### Form4Collector

**Location:** `src/collectors/sec_collector.py`

Collects insider transactions from SEC Form 4 filings.

**Usage:**
```python
from src.collectors import Form4Collector
from datetime import datetime

collector = Form4Collector()
count = collector.collect_historical("AAPL", datetime(2024, 1, 1))
```

**Data Collected:**
- Transaction date
- Shares traded
- Transaction type ('buy' or 'sell')

**Frequency:** Event-driven (irregular)

**Rate Limit:** 60 req/min (SEC EDGAR)

**Library:** `edgartools`

---

## Database Models

**Location:** `src/database/models.py`

All models use SQLAlchemy ORM and work with both SQLite (dev) and PostgreSQL (prod).

### Ticker
```python
class Ticker(Base):
    ticker_id: int                    # Primary key
    symbol: str                       # e.g., "AAPL"
    company_name: str                 # e.g., "Apple Inc."
    created_at: datetime
```

### Price
```python
class Price(Base):
    price_id: int                     # Primary key
    ticker_id: int                    # Foreign key
    date: date                        # Trading date
    open: Decimal                     # Open price
    high: Decimal                     # High price
    low: Decimal                      # Low price
    close: Decimal                    # Close price
    volume: int                       # Volume
    created_at: datetime

# Unique constraint: (ticker_id, date)
# Index: (ticker_id, date)
```

### InstitutionalHolding
```python
class InstitutionalHolding(Base):
    holding_id: int                   # Primary key
    ticker_id: int                    # Foreign key
    filing_date: date                 # When filed
    quarter_end: date                 # Quarter end date
    shares_held: int                  # Shares held
    market_value: Decimal             # Market value
    ownership_percent: Decimal        # Ownership %
    created_at: datetime

# Unique constraint: (ticker_id, quarter_end)
# Index: (ticker_id, quarter_end)
```

### InsiderTransaction
```python
class InsiderTransaction(Base):
    transaction_id: int               # Primary key
    ticker_id: int                    # Foreign key
    transaction_date: date            # Transaction date
    shares_traded: int                # Shares traded
    transaction_type: str             # 'buy' or 'sell'
    created_at: datetime

# Index: (ticker_id, transaction_date)
```

### GoogleTrend
```python
class GoogleTrend(Base):
    trend_id: int                     # Primary key
    ticker_id: int                    # Foreign key
    date: date                        # Date
    search_interest: int              # 0-100 scale
    created_at: datetime

# Unique constraint: (ticker_id, date)
# Index: (ticker_id, date)
```

### RedditSentiment
```python
class RedditSentiment(Base):
    sentiment_id: int                 # Primary key
    ticker_id: int                    # Foreign key
    date: date                        # Date
    mention_count: int                # Daily mentions
    sentiment_score: Decimal          # -1 to +1 scale
    created_at: datetime

# Unique constraint: (ticker_id, date)
# Index: (ticker_id, date)
```

### ZScore
```python
class ZScore(Base):
    z_score_id: int                   # Primary key
    ticker_id: int                    # Foreign key
    date: date                        # Date
    price_z: Decimal                  # Price Z-score
    institutional_z: Decimal          # Institutional Z-score
    retail_search_z: Decimal          # Search Z-score
    retail_sentiment_z: Decimal       # Sentiment Z-score
    created_at: datetime

# Unique constraint: (ticker_id, date)
# Index: (ticker_id, date)
```

### Database Functions

**get_session()**
```python
from src.database import get_session

with get_session() as session:
    ticker = session.query(Ticker).filter(Ticker.symbol == "AAPL").first()
    print(ticker.company_name)
```

**init_db()**
```python
from src.database import init_db

init_db()  # Creates all tables
```

---

## Data Validation

**Location:** `src/validators/data_validator.py`

### DataValidator

Validates data quality and generates reports.

**Usage:**
```python
from src.validators import DataValidator

validator = DataValidator()
report = validator.validate_all()
validator.print_report(report)
```

**Validation Checks:**
- `validate_tickers()` - Ticker whitelist enforcement
- `validate_price_data()` - Price quality (gaps, outliers, invalid values)
- `validate_institutional_data()` - 13F validation
- `validate_insider_data()` - Form 4 validation
- `validate_google_trends()` - Trends validation (0-100 range)
- `validate_reddit_sentiment()` - Sentiment validation (-1 to +1 range)
- `validate_completeness()` - Coverage checks (95% threshold)

**Report Structure:**
```python
{
    'timestamp': datetime,
    'total_issues': int,
    'issues': [
        {
            'severity': 'ERROR' | 'WARNING' | 'INFO',
            'category': 'MISSING_DATA' | 'INVALID_VALUE' | 'OUTLIERS' | ...,
            'message': str,
            'ticker': str,
            'date': date (optional),
            'value': Any (optional)
        }
    ],
    'summary': {
        'by_severity': {'ERROR': 2, 'WARNING': 5, ...},
        'by_category': {'MISSING_DATA': 3, ...},
        'by_ticker': {'AAPL': 1, 'MSFT': 2, ...}
    }
}
```

---

## Configuration

**Location:** `src/config/settings.py`

### Settings

Application configuration loaded from `.env` file.

**Usage:**
```python
from src.config import get_settings

settings = get_settings()  # Cached singleton
print(settings.DATABASE_URL)
print(settings.WHITELISTED_TICKERS)
```

**Key Attributes:**

**Database:**
- `DATABASE_URL` - Connection string
- `DB_POOL_SIZE` - Connection pool size (5)
- `SQL_ECHO` - Enable SQL logging (false)

**Data Collection:**
- `DATA_START_DATE` - Start date (2024-01-01)
- `WHITELISTED_TICKERS` - List of 12 symbols
- `TICKER_COMPANY_MAP` - Symbol → company name mapping

**API Credentials:**
- `REDDIT_CLIENT_ID` - Reddit OAuth client ID
- `REDDIT_CLIENT_SECRET` - Reddit OAuth secret
- `REDDIT_USER_AGENT` - User agent string

**Rate Limits (requests per minute):**
- `SEC_RATE_LIMIT` - 60
- `REDDIT_RATE_LIMIT` - 60
- `GOOGLE_TRENDS_RATE_LIMIT` - 100
- `YAHOO_FINANCE_RATE_LIMIT` - 2000

**Data Processing:**
- `ZSCORE_SHORT_WINDOW` - 30 days
- `ZSCORE_LONG_WINDOW` - 90 days
- `MIN_DATA_POINTS_FOR_ZSCORE` - 14 days
- `MAX_FORWARD_FILL_DAYS` - 3 days
- `IQR_MULTIPLIER` - 1.5 (outlier detection)

**Methods:**

**validate()**
```python
settings.validate()  # Raises ValueError if invalid
```

Checks:
- Reddit credentials are set
- Database URL is configured

**Properties:**
```python
settings.is_development  # True if ENVIRONMENT='development'
settings.is_production   # True if ENVIRONMENT='production'
settings.database_is_sqlite      # True if using SQLite
settings.database_is_postgresql  # True if using PostgreSQL
```

---

## Usage Examples

### Complete Collection Pipeline
```python
from datetime import datetime
from src.collectors import (
    PriceCollector,
    GoogleTrendsCollector,
    RedditCollector,
    Form13FCollector,
    Form4Collector
)
from src.database import init_db
from src.validators import DataValidator
from src.utils import setup_logging

# Setup
setup_logging()
init_db()

start_date = datetime(2024, 1, 1)

# Collect from all sources
collectors = [
    PriceCollector(),
    GoogleTrendsCollector(),
    RedditCollector(),
    Form13FCollector(),
    Form4Collector()
]

for collector in collectors:
    results = collector.collect_all_tickers(start_date)
    print(f"{collector.__class__.__name__}: {sum(results.values())} records")

# Validate
validator = DataValidator()
report = validator.validate_all()
validator.print_report(report)
```

### Query Database
```python
from src.database import get_session, Ticker, Price
from sqlalchemy import func

with get_session() as session:
    # Get ticker
    ticker = session.query(Ticker).filter(Ticker.symbol == "AAPL").first()

    # Count records
    count = session.query(func.count(Price.price_id)).filter(
        Price.ticker_id == ticker.ticker_id
    ).scalar()
    print(f"AAPL has {count} price records")

    # Get recent prices
    prices = session.query(Price).filter(
        Price.ticker_id == ticker.ticker_id
    ).order_by(Price.date.desc()).limit(5).all()

    for price in prices:
        print(f"{price.date}: ${price.close}")
```

### Custom Collector
```python
from src.collectors import BaseCollector
from datetime import datetime

class CustomCollector(BaseCollector):
    def __init__(self):
        super().__init__(rate_limit=60)

    def collect_historical(self, symbol, start_date, end_date=None):
        # Your implementation
        with get_session() as session:
            ticker = self.get_or_create_ticker(session, symbol)

            # Use rate limiter
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed()

            # Fetch data...
            # Insert into database...

            return record_count
```

---

## Rate Limiting

**Location:** `src/utils/rate_limiter.py`

### RateLimiter

Token bucket rate limiter with sliding window.

**Usage:**
```python
from src.utils import RateLimiter

# Create limiter: 60 requests per 60 seconds
limiter = RateLimiter(max_calls=60, period=60)

# Manual usage
limiter.wait_if_needed()
make_api_call()

# Context manager usage
with limiter:
    make_api_call()
```

**Algorithm:**
- Tracks timestamps of recent calls
- Blocks if limit would be exceeded
- Automatically waits until oldest call expires
- Thread-safe (uses locks)

**Example:**
```python
limiter = RateLimiter(max_calls=5, period=60)

for i in range(10):
    with limiter:
        print(f"Request {i+1}")
# Requests 1-5: instant
# Requests 6-10: automatically delayed to respect limit
```

---

## Error Handling

All collectors handle errors gracefully:

**ValueError**
- Raised for invalid ticker (not in whitelist)
- Example: `collector.collect_historical("INVALID", start_date)`

**API Failures**
- Logged with `logger.error()`
- Continues to next ticker
- Returns 0 for failed ticker

**Rate Limit (429)**
- Automatic backoff via `RateLimiter`
- Google Trends: additional 60-second wait
- Logged as warning

**Duplicate Data (IntegrityError)**
- Silently caught and rolled back
- Logged as debug
- Safe to re-run collection

**Network Issues**
- Logged with full traceback
- Continues collection for other tickers
- Check `logs/divergence.log` for details

**Example Error Log:**
```
2025-12-27 21:06:19,042 - src.collectors.price_collector - ERROR - Failed to collect price data for XYZ: Ticker not found
2025-12-27 21:06:19,043 - src.collectors.price_collector - INFO - Collected 0 records for XYZ
```

---

## Logging

**Location:** `src/utils/logging_config.py`

### setup_logging()

Configures application-wide logging.

**Usage:**
```python
from src.utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

logger.info("Starting data collection")
logger.warning("Rate limit approaching")
logger.error("Failed to fetch data", exc_info=True)
```

**Log Outputs:**
- **Console:** Real-time progress (stdout)
- **File:** `logs/divergence.log` (persistent)

**Log Format:**
```
2025-12-27 21:06:19,042 - src.collectors.price_collector - INFO - Collecting price data for AAPL
```

**Log Levels:**
- `DEBUG` - Detailed diagnostic info
- `INFO` - Progress and status updates
- `WARNING` - Non-critical issues
- `ERROR` - Errors that don't stop execution
- `CRITICAL` - Fatal errors

**Configuration:**
Set in `.env` file:
```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Advanced Topics

### Incremental Collection (Phase 2)

All collectors support incremental updates:

```python
# Get last update date from database
with get_session() as session:
    last_price = session.query(Price).order_by(Price.date.desc()).first()
    since_date = last_price.date

# Collect only new data
collector = PriceCollector()
count = collector.collect_incremental("AAPL", since_date)
```

Currently, `collect_incremental()` calls `collect_historical()`. Phase 2 will optimize this.

### Database Migration

**SQLite → PostgreSQL:**

1. Export SQLite data:
```bash
sqlite3 data/divergence.db .dump > backup.sql
```

2. Update `.env`:
```
DATABASE_URL=postgresql://user:pass@host/db
```

3. Run migration:
```bash
python scripts/migrate_to_postgres.py
```

### Adding New Tickers

1. Add to `WHITELISTED_TICKERS` in `src/config/settings.py`
2. Add to `TICKER_COMPANY_MAP`
3. Re-run collection: `python collect_data.py`

### Custom Data Sources

1. Create new collector inheriting from `BaseCollector`
2. Implement `collect_historical()` method
3. Add database model if needed
4. Add to main orchestrator

---

## Performance

**Expected Performance:**
- Price collection: ~30 seconds for all 12 tickers
- Google Trends: ~2-3 minutes (rate limited)
- Reddit: ~5-7 minutes (searches + sentiment)
- SEC 13F: ~1-2 minutes (fewer records)
- SEC Form 4: ~1-2 minutes

**Total:** ~10-15 minutes for complete historical collection

**Database Size:**
- ~148 KB for test data (1 ticker, 499 days)
- ~50-100 MB expected for full dataset (12 tickers, all sources)

**Optimization Tips:**
- Use PostgreSQL for production (better concurrent performance)
- Run collectors in parallel (Phase 2 feature)
- Cache API responses (already implemented)
- Use connection pooling (already implemented)
