# 📊 Project Plan: The Smart Money Divergence Index

## 1. Background & Goals
### **Background**
In modern equity markets, the price of "story stocks" (like **ASTS**) or cyclical giants (like **MU**) is often driven by two distinct forces: institutional accumulation and retail momentum. Institutional investors (Hedge Funds, ETFs) move slowly and based on fundamentals, while retail investors (measured via Google Search trends) often drive high-volatility "hype" cycles. 

This project aims to visualize the tension between these two groups to identify market tops, bottoms, and "smart money" accumulation phases.

### **Goals**
* **Identify Divergence:** Detect periods where retail interest is skyrocketing while institutions are quietly exiting (bearish), or vice versa (bullish).
* **Quantify Sentiment:** Transform unstructured social media text and search trends into a normalized numerical "Hype Score."
* **Interactive Visualization:** Build a web-based dashboard that allows users to toggle between Institutional ownership data and Retail sentiment data over a shared timeline.

---

## 2. Data Stack
To build this index, you need to sync data from three distinct pillars:

### **Pillar A: Institutional Data (The "Smart Money")**
* **SEC Form 13F:** Quarterly holdings for funds managing >$100M (included in Phase 1 MVP).
* **SEC Form 4:** Insider buying/selling by company executives (included in Phase 1 MVP).
* **Source:** SEC EDGAR (via `edgartools`).

### **Pillar B: Retail Data (The "Hype")**
* **Search Volume:** Relative interest over time for specific tickers.
    * *Source:* Google Trends (via `pytrends`).

### **Pillar C: Market Data (The "Truth")**
* **Price & Volume:** Historical OHLCV (Open, High, Low, Close, Volume) data.
* **Source:** Yahoo Finance (via `yfinance`).

---

## 3. Tech Stack
This stack focuses on Python-based tools that transition from data analysis to a production-ready web app.

### **Data Gathering & Engineering**
* **Language:** Python 3.10+
* **APIs/Libraries:**
    * `edgartools` (SEC Filings)
    * `pytrends` (Google Trends)
    * `yfinance` (Stock Prices)
* **Processing:** `Pandas` and `NumPy` (Data cleaning and Z-score normalization).

### **Storage**
* **Database:**
    * **Development:** `SQLite` (local file, zero setup)
    * **Production:** `PostgreSQL` (cloud-hosted, supports concurrent users and deployment)

### **Web App & Visualization**
* **Dashboard Framework:** `Streamlit` (Fastest for Data Analysts).
* **Interactive Charts:** `Plotly` (For synchronized, multi-axis time-series charts).
* **Deployment:** `Streamlit Cloud`.

---

## 4. Analysis Methodology

### **Phase 1 (MVP): Normalization (The Z-Score)**
To compare "Retail Mentions" (integers) with "Institutional Ownership" (percentages) and "Price" (dollars), all metrics will be converted to Z-scores:
$$Z = \frac{(x - \mu)}{\sigma}$$
This allows the dashboard to show how many standard deviations "above normal" a specific metric is at any given time.

**Implementation Details:**
* Rolling windows: 30-day for short-term signals, 90-day for long-term trends
* Outlier detection using IQR (Interquartile Range) method
* Robust statistics (Median Absolute Deviation) for highly skewed data
* Edge case handling for insufficient data, zero variance, and missing values

### **Phase 2: Lead-Lag Correlation Analysis**
After the MVP is complete and validated, the system will add statistical correlation analysis to calculate: *"Does a spike in retail sentiment lead to a price change within 5 days?"*

**Implementation Details:**
* Pearson correlation with time shifts (t+0 to t+5 days)
* 60-day rolling window for correlation calculation
* Statistical significance testing (p-values, confidence intervals)
* Prevents look-ahead bias by using only past data

---

## 5. Development Approach

### **Phase 1 (MVP): Historical Visualization**
**Goal:** Build a working dashboard that visualizes divergence patterns for 12 whitelisted stocks using historical data (2024+).

**Key Components:**
1. **Data Collection Pipeline:** One-time historical data gathering from all sources
2. **Z-Score Normalization:** Statistical engine to make all metrics comparable
3. **Interactive Dashboard:** Streamlit web app with Plotly charts
4. **Data Quality Validation:** Automated checks to ensure accuracy and completeness

### **Phase 2: Automation & Analytics**
**Goal:** Transform the static dashboard into a self-updating system with advanced pattern analysis.

**Key Components:**
1. **Automated Data Sync:** Scheduled jobs for weekly/quarterly updates
2. **Lead-Lag Correlation:** Statistical analysis of retail sentiment vs. price movements

### **Phase 3: Advanced Features (Future)**
**Status:** Out of scope until Phase 1 & 2 are validated with real users.

**Potential Features:**
* Near real-time data integration
* Multi-stock divergence scanner/leaderboard

---

## 6. Technical Challenges & Solutions

### **Data Quality & Validation**
**Challenge:** Ensuring collected data is accurate, complete, and properly filtered.

**Solution:**
* Automated validation pipeline that runs after data collection
* Ticker symbol verification against NYSE/NASDAQ exchange lists
* Outlier flagging for manual review (e.g., search interest >1000% above normal)
* Context validation for ticker mentions (e.g., "MU" must appear in financial context, not as generic word)
* Data completeness checks across all 12 tickers

### **API Rate Limits**
**Challenge:** Respecting rate limits while collecting data from multiple sources.

**Solution:**
* SEC EDGAR: Polite rate limiting (1 request/second recommended)
* Google Trends: Exponential backoff for ~100 requests/hour (unofficial limit)
* Yahoo Finance: Response caching to minimize redundant calls

### **Data Frequency Alignment**
**Challenge:** Different data sources update at different frequencies (13F quarterly, Google Trends weekly, Price daily).

**Solution:**
* 13F Holdings: Quarterly (45-day filing lag) - treat as long-term anchor
* Form 4 Insider: Event-driven - forward-fill to daily
* Google Trends: Weekly data - interpolate to daily for visualization
* Price (OHLCV): Daily - baseline frequency for all visualizations

### **Testing & Reliability**
**Challenge:** Ensuring the dashboard works correctly before deployment.

**Solution:**
* Comprehensive unit tests for data processing and normalization logic (>90% code coverage)
* Integration tests for data fetching and storage (mocked API responses)
* End-to-end tests for complete user workflows
* Performance testing (dashboard load time < 2 seconds)
* Database compatibility testing (SQLite for dev, PostgreSQL for prod)