# Smart Money Divergence Index

A web dashboard that visualizes the divergence between institutional "smart money" and retail "hype" in the stock market to identify potential market opportunities.

## What It Does

This dashboard helps identify market patterns by comparing:
- **Institutional Data (Smart Money):** SEC filings showing what large funds are buying/selling
- **Retail Data (Hype):** Google searches showing retail investor interest
- **Market Data (Truth):** Actual stock prices and what really happened

When institutional and retail investors move in opposite directions, it can signal important market turning points.

## Features

### Phase 1 (MVP) - In Progress
- **Phase 1.1: Data Collection** ✅ Complete
  - ✅ Historical data from 4 sources (2024-present)
  - ✅ 12 stocks tracked (Magnificent 7 + 5 Hype Stocks)
  - ✅ SQLite (dev) / PostgreSQL (prod) database
  - ✅ Automated data validation
  - ✅ Rate limiting & error handling
- **Phase 1.2: Z-Score Engine** 🔜 Next
  - Z-score normalization for comparing metrics
  - Rolling window calculations
  - Outlier handling
- **Phase 1.3: Interactive Dashboard** 🔜 Upcoming
  - Streamlit web interface
  - Plotly visualizations
  - Custom date range selection
  - Toggle data sources on/off
  - Dark theme with educational tooltips

### Phase 2 (Planned)
- Automated weekly/quarterly data refresh
- **Advanced 13F Collection:** "Inverted search" to track institutional ownership from fund filings
- Statistical lead-lag correlation analysis
- Pattern significance testing

### Phase 3 (Future Possibilities)
- Real-time data integration
- Multi-stock scanner and rankings

## Stock Coverage

**Magnificent 7 (Large Cap Tech):**
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google/Alphabet)
- AMZN (Amazon)
- NVDA (NVIDIA)
- META (Meta/Facebook)
- TSLA (Tesla)

**Hype Stocks (High Retail Interest):**
- ASTS (AST SpaceMobile)
- MU (Micron Technology)
- COIN (Coinbase)
- SMCI (Super Micro Computer)
- HOOD (Robinhood)

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "The Smart Money Divergence Index"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows (Git Bash):**
     ```bash
     . venv/Scripts/activate
     ```
     Or alternatively:
     ```bash
     venv/Scripts/activate
     ```
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add your configuration:
   - Database URL (SQLite for development, PostgreSQL for production)

6. **Verify setup:**
   ```bash
   python verify_setup.py
   ```

7. **Collect historical data:**
   ```bash
   python collect_data.py
   ```

8. **(Coming in Phase 1.3) Run the dashboard:**
   ```bash
   streamlit run src/dashboard/app.py
   ```

   The dashboard will open in your browser at `http://localhost:8501`

**See [README.md** - Quick start & overview

## Project Structure

```
The Smart Money Divergence Index/
├── src/
│   ├── data_collection/      # API clients for data sources
│   │   ├── sec_client.py      # SEC EDGAR (13F, Form 4)
│   │   ├── trends_client.py   # Google Trends
│   │   └── market_client.py   # Yahoo Finance prices
│   ├── data_processing/       # Data transformation & normalization
│   │   ├── normalizer.py      # Z-score calculations
│   │   ├── validator.py       # Data quality checks
│   │   └── aggregator.py      # Time series alignment
│   ├── database/              # Database layer
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   └── connection.py      # Database connection & sessions
│   ├── utils/                 # Helper functions
│   │   ├── constants.py       # Ticker lists, settings
│   │   ├── config.py          # Configuration management
│   │   └── logger.py          # Logging setup
│   └── dashboard/             # Streamlit web app
│       ├── app.py             # Main dashboard application
│       ├── components/        # Reusable UI components
│       └── charts.py          # Plotly visualizations
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── scripts/
│   ├── init_db.py             # Database initialization
│   └── collect_data.py        # Data collection script
├── data/
│   ├── raw/                   # Raw API responses (cached)
│   ├── processed/             # Cleaned data
│   └── divergence.db          # SQLite database (dev)
├── logs/                      # Application logs
├── docs/                      # Documentation
│   ├── FEATURE-PLAN.md        # User-facing feature descriptions
│   └── TECHNICAL-SPEC.md      # Technical implementation details
├── .env                       # Environment variables (not in git)
├── .env.example               # Template for environment variables
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## Technology Stack

- **Language:** Python 3.10+
- **Database:** SQLite (development) / PostgreSQL (production)
- **ORM:** SQLAlchemy
- **Web Framework:** Streamlit
- **Visualization:** Plotly
- **Data Sources:**
  - SEC EDGAR via edgartools
  - Google Trends via pytrends
  - Yahoo Finance via yfinance
- **Testing:** pytest
- **Code Quality:** black, flake8, mypy

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m e2e         # End-to-end tests only
```

### Code Formatting
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Database Management

**SQLite (Development):**
```bash
# Database is automatically created in data/divergence.db
# No additional setup needed
```

**PostgreSQL (Production):**
```bash
# Update .env with PostgreSQL connection string
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"
```

## Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```env
# Database
DATABASE_URL=sqlite:///data/divergence.db  # Development
# DATABASE_URL=postgresql://user:pass@host:5432/dbname  # Production

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
DATA_START_DATE=2024-01-01
```

## Data Sources & Rate Limits

| Source | Data Type | Frequency | Rate Limit | Authentication |
|--------|-----------|-----------|------------|----------------|
| SEC EDGAR | Institutional holdings, insider trades | Quarterly/Event-driven | ~1 req/sec | None |
| Google Trends | Search interest | Weekly | ~100 req/hour | None |
| Yahoo Finance | Price, volume | Daily | Unlimited | None |

## Contributing

This is a portfolio project. Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

### Project Documentation
- **[Feature Plan](docs/FEATURE-PLAN.md)** - User-facing features and product roadmap
- **[Technical Specification](docs/TECHNICAL-SPEC.md)** - Implementation details and architecture

### Phase 1 Data Collection (✅ Complete)
- **[README](docs/phase1-data-collection/README.md)** - Quick start & overview
- **[DATA_COLLECTION.md](docs/phase1-data-collection/DATA_COLLECTION.md)** - Complete technical reference

## Phase 1 Progress

Track Phase 1 MVP completion:

- [x] **Phase 1.1: Data Collection** ✅ Complete
  - [x] Database setup (SQLite & PostgreSQL support)
  - [x] Data collection pipeline for 4 sources (Price, Google Trends, SEC 13F, SEC Form 4)
  - [x] Data quality validation
  - [x] Comprehensive test suite
  - [x] Full documentation
- [ ] **Phase 1.2: Z-Score Engine** 🔜 Next
  - [ ] Z-score normalization engine
  - [ ] Rolling window calculations
  - [ ] Outlier handling
- [ ] **Phase 1.3: Dashboard** 🔜 Upcoming
  - [ ] Interactive Streamlit dashboard
  - [ ] Plotly visualizations
  - [ ] Deployment to Streamlit Cloud

## Troubleshooting

**Issue:** `ModuleNotFoundError` when running scripts
- **Solution:** Ensure virtual environment is activated and dependencies are installed

**Issue:** Database connection error
- **Solution:** Check `DATABASE_URL` in `.env` file and ensure database exists

**Issue:** No data showing in dashboard
- **Solution:** Run `python scripts/collect_data.py` to collect historical data first

## License

MIT License - See [LICENSE](LICENSE) file for details

## Disclaimer

This tool is for educational and analytical purposes only. It does not provide financial advice. Always do your own research and consult with financial professionals before making investment decisions.

## Contact & Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Built with:** Python • Streamlit • Plotly • SQLAlchemy • PostgreSQL
