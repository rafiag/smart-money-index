# Phase 1.1: Data Collection Pipeline

## Overview

Complete data collection system for the Smart Money Divergence Index. Collects historical data from 5 sources for 12 stocks (2024-present).

**Status:** ✅ Complete and tested

## Quick Start

### 1. Setup (5 minutes)

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure Reddit API
# Get credentials: https://www.reddit.com/prefs/apps
# Edit .env file and add:
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
```

### 2. Verify Setup

```bash
python verify_setup.py
```

**Expected output:**
```
✓ Environment: development
✓ Database: sqlite
✓ All checks passed!
```

### 3. Collect Data

```bash
python collect_data.py
```

**What happens:**
- Creates database (`data/divergence.db`)
- Collects data for 12 stocks from 5 sources
- Validates data quality
- Shows summary report

**Expected runtime:** 10-15 minutes

### 4. Verify Results

```bash
# Check database
sqlite3 data/divergence.db "SELECT COUNT(*) FROM prices;"

# View logs
cat logs/divergence.log
```

## What Was Built

### Data Sources (5)
1. **Yahoo Finance** - Daily OHLCV prices
2. **Google Trends** - Search interest (0-100)
3. **Reddit** - Sentiment from r/wallstreetbets, r/stocks, r/investing
4. **SEC 13F** - Institutional holdings (quarterly)
5. **SEC Form 4** - Insider transactions (event-driven)

### Stock Coverage (12)
**Magnificent 7:** AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA
**Hype Stocks:** ASTS, MU, COIN, SMCI, HOOD

### Key Features
- ✅ **Rate Limiting** - Respects API limits automatically
- ✅ **Error Handling** - Graceful failures, continues on errors
- ✅ **Duplicate Prevention** - Safe to re-run anytime
- ✅ **Data Validation** - Automated quality checks
- ✅ **Database Abstraction** - SQLite (dev) / PostgreSQL (prod)
- ✅ **Comprehensive Logging** - File + console output
- ✅ **Tested** - Unit and integration tests passing

## Project Structure

```
src/
├── collectors/              # 5 data collectors
│   ├── base.py             # Base class with common functionality
│   ├── price_collector.py  # Yahoo Finance integration
│   ├── google_trends_collector.py  # Google Trends with interpolation
│   ├── reddit_collector.py # Reddit sentiment analysis
│   └── sec_collector.py    # SEC 13F & Form 4
├── database/               # SQLAlchemy ORM
│   ├── base.py            # Connection & session management
│   └── models.py          # 7 database tables
├── validators/            # Data quality checks
│   └── data_validator.py  # Validation & reporting
├── config/                # Configuration
│   └── settings.py        # Environment-based settings
└── utils/                 # Shared utilities
    ├── logging_config.py  # Logging setup
    └── rate_limiter.py    # API rate limiting

tests/
├── unit/                  # Unit tests
│   ├── test_config.py
│   └── test_rate_limiter.py
└── integration/           # Integration tests
    └── test_database.py

Scripts:
├── collect_data.py        # Main orchestrator
└── verify_setup.py        # Setup verification
```

## Database Schema

**7 Tables:**
- `tickers` - Stock symbols and company names
- `prices` - Daily OHLCV data
- `institutional_holdings` - SEC 13F quarterly data
- `insider_transactions` - SEC Form 4 insider trades
- `google_trends` - Daily search interest
- `reddit_sentiment` - Daily mentions and sentiment
- `z_scores` - Normalized metrics (Phase 1.2)

**Example queries:**
```sql
-- Check data coverage
SELECT symbol, COUNT(*) FROM prices
JOIN tickers USING (ticker_id)
GROUP BY symbol;

-- View recent prices
SELECT * FROM prices
JOIN tickers USING (ticker_id)
WHERE symbol = 'AAPL'
ORDER BY date DESC LIMIT 5;
```

## Configuration

**Environment Variables** (`.env` file):

```bash
# Database
DATABASE_URL=sqlite:///data/divergence.db  # Dev
# DATABASE_URL=postgresql://user:pass@host/db  # Prod

# Reddit API (required for sentiment data)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret

# Data Collection
DATA_START_DATE=2024-01-01

# Rate Limits (requests per minute)
SEC_RATE_LIMIT=60
REDDIT_RATE_LIMIT=60
GOOGLE_TRENDS_RATE_LIMIT=100
YAHOO_FINANCE_RATE_LIMIT=2000
```

**Get Reddit Credentials:**
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" → Choose "script"
3. Copy client ID and secret
4. Add to `.env` file

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/
pytest tests/integration/
```

**Test results:** All passing ✅

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Reddit credentials not set | Configure `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env` |
| Rate limit (429) error | Wait 1-2 minutes, script has automatic backoff |
| Database locked | Close any database browser tools |
| Import errors | Activate virtual environment: `venv\Scripts\activate` |
| No data for ticker | Check validation report, some tickers have limited history |

**Check logs:** `logs/divergence.log` for detailed errors

## Architecture Highlights

### Scalable Design (Phase 2 Ready)
- All collectors have `collect_incremental()` methods (ready to optimize)
- Database tracks timestamps for delta queries
- Rate limiting infrastructure built-in
- SQLite → PostgreSQL swap with zero code changes
- Modular design (easy to add sources/tickers)

### Production-Ready
- Comprehensive error handling
- Automatic retry with exponential backoff
- Data validation with detailed reporting
- Database transaction management
- Professional logging

### Well-Tested
- Unit tests for core logic
- Integration tests for database operations
- Real data collection verified (499 days for AAPL)

## Next Steps

**After data collection:**
1. Review validation report for any issues
2. Explore database with SQL queries
3. **Phase 1.2:** Build Z-score normalization engine
4. **Phase 1.3:** Build interactive dashboard

## Documentation

- **[DATA_COLLECTION.md](DATA_COLLECTION.md)** - Complete technical reference
- **[../../TECHNICAL-SPEC.md](../TECHNICAL-SPEC.md)** - Full technical specification
- **[../../FEATURE-PLAN.md](../FEATURE-PLAN.md)** - User-facing features

## Support

For issues:
1. Run `verify_setup.py` to diagnose
2. Check `logs/divergence.log` for errors
3. Review `DATA_COLLECTION.md` for technical details
