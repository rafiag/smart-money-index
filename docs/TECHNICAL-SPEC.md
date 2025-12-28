# Technical Specification: Smart Money Divergence Index

## Document Purpose
This document contains detailed implementation specifications for developers. For user-facing feature descriptions, see FEATURE-PLAN.md.

---

## Phase 1: MVP Technical Implementation

### 1.1 Static Data Collection Pipeline

**Technology Stack:**
*   **Database:**
    *   **Development:** SQLite (local file-based database, zero configuration)
    *   **Production:** PostgreSQL (cloud-hosted, supports concurrent users)
    *   **Strategy:** SQLAlchemy ORM abstracts database layer - same code works with both
*   **ORM:** SQLAlchemy for database abstraction and migrations
*   **APIs:** edgartools (SEC), pytrends (Google Trends), yfinance (Market Data)

**API Rate Limits & Strategy:**
*   **SEC EDGAR:** No authentication, polite rate limiting (1 request/second recommended)
*   **Google Trends:** ~100 requests/hour (unofficial), implement exponential backoff
*   **Yahoo Finance:** No official limit, cache responses to minimize redundant calls

**Data Frequency Alignment:**
*   **Phase 2 - 13F Holdings (Inverted Search):** Quarterly (45-day lag) - requires inverted search of fund filings
*   **Form 4 Insider:** Event-driven (irregular) - forward-fill to daily
*   **Google Trends:** Weekly data - interpolate to daily for visualization
*   **Price (OHLCV):** Daily - baseline frequency for all visualizations

**Data Refresh Strategy:**
*   **Phase 1:** One-time historical collection (2024-01-01 to present)
*   **Phase 2:** Incremental updates (fetch only new data since last run)
*   **Design Note:** Build with incremental logic from start to avoid Phase 2 refactoring

**Testing Requirements:**
*   Verify data completeness for all 12 tickers
*   Validate data format consistency
*   Handle missing data points gracefully
*   Test API failure scenarios with mocked responses
*   Database connection and persistence validation
*   Rate limit compliance verification
*   Temporal alignment accuracy (weekly → daily interpolation)

---

### 1.2 The Z-Score Normalization Engine

**Formula:** `Z = (x - μ) / σ` where μ = rolling mean, σ = rolling standard deviation

**Statistical Implementation Details:**

**Rolling Window:**
**Rolling Window:**
*   30-day lookback for Price (Daily)
*   4-week lookback for Trends (Weekly)
*   4-quarter (1-year) lookback for Holdings (Quarterly)
*   *Rationale:* Frequency-specific windows prevent statistical artifacts from upsampling.

**Outlier Detection:**
*   **Strategy:** Apply hard clipping (Winsorization) to the input data before Z-score calculation.
*   **Thresholds:** Cap values at 1st and 99th percentiles (rolling or global).
*   **Rationale:** Prevents extreme "meme stock" volality from flattening the entire history's Z-scores.

**Robust Statistics Alternative:**
*   For highly skewed data, use Median Absolute Deviation (MAD) instead of standard deviation
*   Formula: `Robust Z = (x - median) / MAD`

**Edge Case Handling:**
*   **Insufficient Data:** Require minimum 14 days of data before calculating Z-scores
*   **Zero Variance:** If σ = 0 (flat period), return Z = 0 instead of division error
*   **Missing Values:** 
    *   Forward-fill up to 7 days for Weekly Trends (allow 1 week gap)
    *   Forward-fill up to 95 days for Quarterly Holdings (allow 1 quarter gap)
    *   Do not interpolate across large gaps > limit.

**Testing Requirements:**
*   Unit tests for Z-score calculation accuracy (compare to manual calculations)
*   Edge case handling (zero variance, single data points, all nulls)
*   Outlier detection validation (verify IQR flagging logic)
*   Robust statistics comparison (MAD vs standard deviation for skewed data)
*   Rolling window boundary conditions (first 30 days of data)

---

### 1.3 Interactive Dashboard Technical Stack

**Framework Stack:**
*   **Framework:** Streamlit (Python-based web apps, fast iteration)
*   **Charts:** Plotly (interactive JavaScript visualizations)
*   **Deployment:** Streamlit Cloud (free tier for MVP)
*   **Styling:** Streamlit theming + custom CSS for dark mode

**Performance Requirements:**
*   Dashboard load time < 2 seconds for any ticker/date range combination
*   Chart rendering < 500ms
*   Interactive updates (toggle, date change) < 300ms

**Testing Requirements:**
*   End-to-end user workflow testing
*   Responsive design validation (desktop and mobile)
*   Chart interactivity verification (zoom, pan, hover)
*   Tooltip content accuracy
*   Performance testing (dashboard load time < 2 seconds)

---

### 1.4 Data Quality Validation

**Validation Rules:**
*   **Ticker Symbol Validation:** Verify against NYSE/NASDAQ exchange lists (prevent typos like "APLE" instead of "AAPL")
*   **Missing Data Detection:** Flag gaps in time series (weekends/holidays expected, weekdays require investigation)
*   **Outlier Flagging:** Identify extreme values for manual review (e.g., search interest >1000% above normal)
*   **Data Completeness:** Ensure all 12 tickers have data for all expected dates
*   **Type Validation:** Verify data types (dates are datetime, prices are float, tickers are string)
*   **Range Checks:** Prices > 0, ownership percentages 0-100%, search interest 0-100

**Ticker Disambiguation:**
*   **"MU" Filter:** Ensure "MU" refers to Micron Technology (ticker: MU) not generic word usage
*   **Context Validation:** Verify ticker appears in financial context (not random mentions)

**Testing Requirements:**
*   Unit tests for each validation rule
*   Integration tests with real API responses (including malformed data)
*   Edge case handling (market holidays, API failures, partial data)
*   Validation report generation (summary of flagged issues)
*   False positive rate testing (ensure valid data isn't incorrectly flagged)

---

## Phase 1 Definition of Done

**Phase 1 is complete when:**
- [x] All 12 tickers have complete 2024+ data in database
- [x] Database works correctly in both SQLite (dev) and PostgreSQL (prod) modes
- [x] Z-scores calculated correctly (validated against manual calculations for sample data)
- [ ] Dashboard loads in <2 seconds for any ticker/date range combination
- [x] All unit tests passing (>90% code coverage)
- [x] All integration tests passing (mocked API responses)
- [ ] End-to-end user workflow completes without errors
- [ ] Data quality validation reports show <5% flagged issues
- [ ] Educational tooltips reviewed for accuracy by finance-knowledgeable reviewer
- [ ] Dark theme renders correctly on desktop and mobile browsers
- [ ] Successfully deployed to Streamlit Cloud with PostgreSQL
- [ ] Documentation updated (README.md reflects current state with setup instructions for both databases)

---

## Phase 2: Automation & Scalability Technical Implementation

### 2.1 Automated Data Sync (The "Crawler")

**Architecture:**
*   **Scheduler:** Use APScheduler or Celery for job scheduling
*   **Job Frequency:**
    *   Weekly updates for Retail/Market data (Google Trends, Price)
    *   Quarterly updates for Institutional data (13F filings)
*   **Incremental Logic:** Query database for last update timestamp, fetch only newer data
*   **Error Recovery:** Implement retry logic with exponential backoff
*   **Monitoring:** Log all job executions with success/failure status

**Testing Requirements:**
*   Scheduled job reliability testing
*   API failure recovery validation
*   Rate limit compliance verification
*   Data integrity checks after updates

---

### 2.2 Statistical Lead-Lag Correlation

**Statistical Methodology:**
*   **Correlation Type:** Pearson correlation with time shifts (t+0 to t+5 days)
*   **Sliding Window:** 60-day rolling window for correlation calculation
*   **Significance Testing:** Report p-values (require p < 0.05 for statistical significance)
*   **Confidence Intervals:** Bootstrap 95% confidence intervals for correlation estimates
*   **Multiple Testing Correction:** Bonferroni correction when testing multiple time lags
*   **Autocorrelation Check:** Test for autocorrelation before correlation analysis (Durbin-Watson test)
*   **Look-Ahead Bias Prevention:** Ensure correlation uses only past data (no future information leakage)

**Performance Requirements:**
*   Correlation calculation < 500ms per ticker
*   Dashboard update < 1 second when toggling correlation panel

**Testing Requirements:**
*   Statistical accuracy validation (compare to scipy.stats results)
*   Performance benchmarking (correlation calculation < 500ms per ticker)
*   Edge case handling (insufficient data, flat periods, perfect correlation)
*   Autocorrelation detection accuracy (Durbin-Watson test validation)
*   Confidence interval coverage testing (bootstrap validation)
*   Look-ahead bias testing (verify no future data usage)
*   Multiple testing correction verification (Bonferroni adjustment)

---

## Phase 2 Definition of Done

**Phase 2 is complete when:**
- [ ] Automated data sync runs successfully on schedule (weekly for retail/market, quarterly for institutional)
- [ ] Incremental updates fetch only new data (verified by database query logs)
- [ ] API rate limit compliance verified (no 429 errors in logs)
- [ ] Data integrity maintained after automated updates (no duplicates, no missing dates)
- [ ] Lead-lag correlation calculations complete in <500ms per ticker
- [ ] Statistical significance properly reported (p-values, confidence intervals)
- [ ] Correlation insights panel displays correctly in dashboard
- [ ] All Phase 1 features still work after automation integration
- [ ] Error handling tested (API failures, network issues, malformed data)
- [ ] Monitoring/logging system captures all automated job statuses
- [ ] Documentation updated with automation architecture and troubleshooting guide

---

## Phase 3: Advanced Features Technical Implementation

**Status:** OUT OF SCOPE until Phase 1 and 2 are validated with real users.

### 3.1 Near Real-Time Data Integration

**Infrastructure Requirements:**
*   WebSocket or Server-Sent Events for real-time updates
*   Streaming data architecture (Apache Kafka or similar)
*   Cloud hosting with scalable resources (AWS, GCP, or Azure)
*   Advanced query optimization (materialized views, indexing strategy)
*   Caching layer (Redis) for frequently accessed data

**Performance Requirements:**
*   Data latency < 1 minute from source to dashboard
*   Dashboard update < 500ms after new data arrival
*   Support 100+ concurrent users

---

### 3.2 Divergence Leaderboard & Scanner

**Database Optimization:**
*   Materialized views for pre-computed divergence scores
*   Refresh strategy: Update every 15 minutes
*   Composite indexes on (ticker, date, divergence_score)

**Ranking Algorithm:**
*   Calculate divergence score = |Institutional Z-score - Retail Z-score|
*   Sort by divergence score descending
*   Return top 3 "overhyped" (retail > institutional) and "under-accumulated" (institutional > retail)

**Performance Requirements:**
*   Multi-ticker query < 1 second
*   Leaderboard page load < 2 seconds

---

## Database Schema

**Note:** Schema is defined using SQLAlchemy ORM models, which automatically work with both SQLite (development) and PostgreSQL (production). SQL examples below show PostgreSQL syntax for reference.

### Core Tables

**tickers**
```sql
CREATE TABLE tickers (
    ticker_id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**prices**
```sql
CREATE TABLE prices (
    price_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker_id, date)
);
```

**institutional_holdings**
```sql
CREATE TABLE institutional_holdings (
    holding_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    filing_date DATE NOT NULL,
    quarter_end DATE NOT NULL,
    shares_held BIGINT,
    market_value DECIMAL(15, 2),
    ownership_percent DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker_id, quarter_end)
);
```

**insider_transactions**
```sql
CREATE TABLE insider_transactions (
    transaction_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    transaction_date DATE NOT NULL,
    shares_traded BIGINT,
    transaction_type VARCHAR(20), -- 'buy' or 'sell'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**google_trends**
```sql
CREATE TABLE google_trends (
    trend_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    date DATE NOT NULL,
    search_interest INTEGER, -- 0-100 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker_id, date)
);
```

**z_scores**
```sql
CREATE TABLE z_scores (
    z_score_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    date DATE NOT NULL,
    price_z DECIMAL(6, 3),
    institutional_z DECIMAL(6, 3),
    retail_search_z DECIMAL(6, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker_id, date)
);
```

### Indexes

```sql
CREATE INDEX idx_prices_ticker_date ON prices(ticker_id, date);
CREATE INDEX idx_institutional_ticker_quarter ON institutional_holdings(ticker_id, quarter_end);
CREATE INDEX idx_trends_ticker_date ON google_trends(ticker_id, date);
CREATE INDEX idx_zscores_ticker_date ON z_scores(ticker_id, date);
```

---

## Development Sequence

### Phase 1 (MVP) - Build Order
1. **Database Setup** → PostgreSQL installation, schema creation, migrations
2. **Static Pipeline** → API integration, data collection scripts
3. **Data Quality Validation** → Validation pipeline, error reporting
4. **Z-Score Engine** → Statistical calculations, outlier handling
5. **Interactive UI** → Streamlit dashboard, Plotly charts
6. **Comprehensive Testing** → Unit tests, integration tests, E2E tests

**Visual Dependency Flow:**
```
[Database Setup] → [Static Pipeline] → [Data Quality] → [Z-Score Engine] → [Interactive UI] → [Testing]
       ↓                    ↓                ↓                ↓                    ↓              ↓
  (PostgreSQL)          (API Calls)    (Validation)    (Normalization)      (Streamlit)    (Unit/E2E)
       ↓                    ↓                ↓                ↓                    ↓              ↓
   (SQLAlchemy)        (Rate Limits)  (Ticker Check)   (IQR Outliers)       (Plotly)      (Coverage)
```

### Phase 2 (Automation) - Build Order
1. **Job Scheduler Setup** → APScheduler/Celery configuration
2. **Incremental Update Logic** → Modified data collection for deltas
3. **Automated Sync** → Scheduled jobs, error recovery
4. **Statistical Engine** → Correlation calculations, significance testing
5. **Lead-Lag Analytics UI** → New dashboard panel
6. **Integration Testing** → Ensure automation doesn't break existing features

**Visual Dependency Flow:**
```
[Phase 1 Complete] → [Job Scheduler] → [Incremental Logic] → [Automated Sync] → [Statistical Engine] → [Lead-Lag UI] → [Testing]
                           ↓                    ↓                      ↓                    ↓                  ↓              ↓
                   (APScheduler)          (Delta Queries)      (Scheduled Jobs)    (Correlation)      (Dashboard Panel)  (Regression)
                           ↓                    ↓                      ↓                    ↓                  ↓              ↓
                    (Cron/Celery)         (Last Updated)       (Error Recovery)    (Bootstrap CI)      (Plotly Viz)   (Performance)
```

### Phase 3 (Advanced) - Build Order
*To be determined based on user feedback and demand validation*

**Potential Sequence (if pursued):**
1. **Streaming Infrastructure** → WebSocket/SSE setup, message queues
2. **Live Data Integration** → Real-time price feeds, sentiment streams
3. **Materialized Views** → Pre-computed divergence scores
4. **Stock Scanner UI** → Multi-ticker overview dashboard
5. **Performance Optimization** → Caching, query optimization, load testing

---

## Technology Decisions Log

### Database: SQLite (Dev) + PostgreSQL (Prod)
**Rationale:**
- **SQLite for Development:** Zero configuration, fast iteration, simple testing, works offline, database is just a file
- **PostgreSQL for Production:** Supports concurrent users, cloud-friendly, strong community support, handles time-series data well
- **SQLAlchemy Abstraction:** Same codebase works with both databases, swap via configuration change
**Alternatives Considered:** PostgreSQL-only (overkill for local dev), TimescaleDB (over-engineering for MVP).

### ORM: SQLAlchemy
**Rationale:** Industry standard, excellent documentation, handles migrations, abstracts database layer for testing.
**Alternatives Considered:** Django ORM (requires full Django), Raw SQL (harder to maintain).

### Dashboard: Streamlit
**Rationale:** Python-native, fast prototyping, built-in deployment, minimal frontend code.
**Alternatives Considered:** Dash (more verbose), Flask + React (over-engineering).

### Charts: Plotly
**Rationale:** Interactive out-of-box, syncs with Streamlit, supports multi-axis charts, responsive.
**Alternatives Considered:** Matplotlib (not interactive), Chart.js (requires JavaScript).

### Testing: pytest
**Rationale:** Standard Python testing framework, excellent plugin ecosystem, fixtures for database testing.
**Alternatives Considered:** unittest (more verbose), nose (unmaintained).

---

## Deployment Architecture

### Development (Local)
```
Local Machine
    ↓
SQLite Database (stored as file: data/divergence.db)
    ↓
Git Version Control
```

### MVP Deployment (Phase 1)
```
Streamlit Cloud (Free Tier)
    ↓
Hosted PostgreSQL (Render/Railway Free Tier)
    ↓
GitHub Repository (version control, CI/CD)
```

**Environment Configuration:**
- Development: `DATABASE_URL=sqlite:///data/divergence.db`
- Production: `DATABASE_URL=postgresql://user:pass@host:5432/dbname`

### Production (Phase 2+)
```
Streamlit Cloud (Paid Tier) OR Self-hosted
    ↓
PostgreSQL (Managed Service: RDS/Cloud SQL)
    ↓
Background Jobs (Celery + Redis)
    ↓
Monitoring (Sentry for errors, Datadog for metrics)
```

---

## Security Considerations

### API Keys
*   Store in environment variables (never commit to Git)
*   Use `.env` file for local development (add to `.gitignore`)
*   Use Streamlit Secrets for production deployment

### Database Access
*   **Development (SQLite):** File-based, no authentication, restrict file permissions to user only
*   **Production (PostgreSQL):** Restrict database user permissions (read-only for dashboard, read-write for sync jobs)
*   Use connection pooling (SQLAlchemy default)
*   Enable SSL connections for production PostgreSQL instances
*   Never commit SQLite database file to Git (add to `.gitignore`)

### Input Validation
*   Whitelist ticker symbols (only allow 12 defined tickers)
*   Validate date ranges (2024-01-01 to current date)
*   Sanitize user inputs before database queries (SQLAlchemy parameterization)

### Rate Limiting
*   Implement request throttling for API calls
*   Cache API responses to minimize redundant calls
*   Respect API provider rate limits to avoid IP bans
