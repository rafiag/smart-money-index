# Installation Guide

## Quick Start (Recommended)

### Step 1: Upgrade pip first
```bash
python -m pip install --upgrade pip
```

### Step 2: Install minimal dependencies
```bash
pip install -r requirements-minimal.txt
```

### Step 3: Install remaining dependencies (optional)
```bash
pip install -r requirements.txt
```

---

## Troubleshooting Installation Issues

### Issue: "pip subprocess to install build dependencies did not run successfully"

**Solution 1: Install packages individually**

If a package fails, install the core packages one by one:

```bash
# Core data science
pip install pandas numpy scipy

# Database
pip install sqlalchemy alembic

# Dashboard
pip install streamlit plotly

# Data sources (try each separately)
pip install yfinance
pip install praw
pip install pytrends
pip install edgartools

# Utilities
pip install python-dotenv requests
```

**Solution 2: Skip problematic packages for now**

Some packages are only needed for specific features:
- `psycopg2-binary` - Only needed for PostgreSQL (use SQLite for now)
- `celery`, `redis`, `apscheduler` - Only needed for Phase 2 automation
- `lxml` - Only needed if web scraping is required
- `nltk`, `textblob`, `vaderSentiment` - Only for advanced sentiment analysis

**Solution 3: Use a different Python version**

Python 3.14 is very new. Consider using Python 3.10, 3.11, or 3.12 which have better package support:

1. Download Python 3.12 from python.org
2. Install it
3. Create a new virtual environment:
   ```bash
   python3.12 -m venv venv
   ```
4. Activate and try again

---

## Platform-Specific Issues

### Windows: psycopg2-binary fails

If PostgreSQL adapter fails to install:
1. Skip it for now (use SQLite): Remove `psycopg2-binary` from requirements
2. Or install PostgreSQL binaries separately from postgresql.org

### Windows: lxml fails

If lxml fails:
```bash
pip install --only-binary :all: lxml
```

Or skip it - it's only needed for certain web scraping tasks.

---

## Minimal Working Setup

To get the dashboard running with minimal dependencies:

```bash
# Essential packages only
pip install pandas numpy sqlalchemy python-dotenv streamlit plotly yfinance praw

# Skip these for now:
# - psycopg2-binary (use SQLite instead)
# - celery, redis, apscheduler (Phase 2 only)
# - nltk, textblob, vaderSentiment (basic sentiment is fine)
# - testing and dev tools (install later)
```

Update your `.env` to use SQLite:
```
DATABASE_URL=sqlite:///data/divergence.db
```

---

## Verify Installation

After installing, verify everything works:

```bash
python -c "import pandas, numpy, sqlalchemy, streamlit, plotly; print('✓ Core packages installed')"
python -c "import praw, yfinance; print('✓ Data source packages installed')"
```

---

## Next Steps

Once you have the minimal packages installed:
1. Set up your `.env` file (copy from `.env.example`)
2. Run database initialization (when ready)
3. Start the dashboard to verify it loads

You can always install additional packages later as needed!
