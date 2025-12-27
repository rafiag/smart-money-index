# Smart Money Divergence Index - Deployment Checklist

## Phase 1: Initial Setup & Configuration

### 1. Environment Setup
- [x] Python 3.11+ installed
- [x] Virtual environment created (`python -m venv venv`)
- [x] Virtual environment activated
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] Git repository initialized
- [x] `.gitignore` configured (exclude `.env`, `data/`, `__pycache__/`)

### 2. Database Setup
- [ ] SQLite database directory created (`data/` folder)
- [ ] Database URL configured in `.env`:
  - [ ] Development: `DATABASE_URL=sqlite:///data/divergence.db`
  - [ ] Production: PostgreSQL URL (if applicable)
- [ ] Database tables created: `python -m src.database.init_db`
- [ ] Database connection tested

### 4. Environment Variables Configuration
Review and configure `.env` file:

#### Required Settings
- [ ] `DATABASE_URL` - Database connection string

#### Optional Settings (Review Defaults)
- [ ] `ENVIRONMENT` - development or production (default: development)
- [ ] `LOG_LEVEL` - DEBUG, INFO, WARNING, ERROR (default: INFO)
- [ ] `DATA_START_DATE` - Historical data start date (default: 2024-01-01)
- [ ] `ENABLE_CACHING` - Enable API response caching (default: true)
- [ ] `CACHE_EXPIRY_HOURS` - Cache expiration time (default: 24)

#### Rate Limiting (Verify Defaults)
- [ ] `SEC_RATE_LIMIT` - SEC EDGAR requests/min (default: 30)
- [ ] `GOOGLE_TRENDS_RATE_LIMIT` - Google Trends requests/hour (default: 100)
- [ ] `YAHOO_FINANCE_RATE_LIMIT` - Yahoo Finance requests/min (default: 2000)

---

## Phase 2: Data Collection

### 5. Test Individual Data Collectors
- [ ] Test SEC Form 13F collector: `python test_sec_collector.py`
- [ ] Test SEC Form 4 collector: `python test_form4_collector.py`
- [ ] Test Google Trends collector: `python test_trends_collector.py`
- [ ] Test Yahoo Finance collector: `python test_price_collector.py`

### 6. Initial Historical Data Collection
Run collectors for all 12 whitelisted tickers (2024 onward):

**Institutional Data**
- [ ] Collect 13F filings: `python -m src.collectors.sec_collector`
- [ ] Collect Form 4 insider transactions: `python -m src.collectors.form4_collector`

**Retail Data**
- [ ] Collect Google Trends data: `python -m src.collectors.trends_collector`

**Market Data**
- [ ] Collect price/volume data: `python -m src.collectors.price_collector`

### 7. Verify Data Collection
- [ ] Check database for collected data: `python verify_data.py`
- [ ] Verify all 12 tickers have data
- [ ] Verify date ranges (2024-01-01 to present)
- [ ] Check for data gaps or anomalies
- [ ] Review logs for errors or warnings

---

## Phase 3: Data Processing & Analysis

### 8. Data Processing Pipeline
- [ ] Run data validation: Check for missing values, outliers
- [ ] Calculate Z-scores for normalization
- [ ] Verify Z-score calculations are correct
- [ ] Test divergence detection algorithms
- [ ] Generate test visualizations

### 9. Quality Assurance
- [ ] Run unit tests: `pytest tests/unit/`
- [ ] Run integration tests: `pytest tests/integration/`
- [ ] Run end-to-end tests: `pytest tests/e2e/`
- [ ] Verify all tests pass
- [ ] Check code coverage (aim for >80%)

---

## Phase 4: Dashboard Development

### 10. Streamlit Dashboard Setup
- [ ] Streamlit installed: `pip install streamlit`
- [ ] Dashboard file created: `src/dashboard/app.py`
- [ ] Dashboard runs locally: `streamlit run src/dashboard/app.py`
- [ ] Test ticker selection dropdown (12 tickers)
- [ ] Test date range filtering
- [ ] Test data source toggles (institutional/retail/price)
- [ ] Verify interactive charts render correctly
- [ ] Test tooltips and educational content
- [ ] Verify dark theme with blue/green accents
- [ ] Test on different screen sizes

### 11. Dashboard Features Checklist
- [ ] Ticker selector (dropdown with 12 stocks)
- [ ] Date range picker (2024 onward)
- [ ] Data source toggles (institutional/retail/price on/off)
- [ ] Interactive Plotly chart with:
  - [ ] Institutional data layer (blue)
  - [ ] Retail sentiment layer (green)
  - [ ] Price data layer (orange)
  - [ ] Synchronized time axis
  - [ ] Zoom/pan functionality
  - [ ] Hover tooltips
- [ ] Educational text explaining divergence
- [ ] Loading states/spinners
- [ ] Error handling and user-friendly messages
- [ ] Performance optimization (chart loads < 3 seconds)

---

## Phase 5: Production Deployment (Optional)

### 12. GitHub Repository Setup
- [ ] GitHub repository created (public or private)
- [ ] README.md written with:
  - [ ] Project description
  - [ ] Setup instructions
  - [ ] Usage guide
  - [ ] Screenshot/demo
- [ ] `.env.example` file created (with placeholder values)
- [ ] All code committed and pushed
- [ ] Repository URL documented

### 13. PostgreSQL Database (Production)
- [ ] PostgreSQL database provisioned (Render/Railway/Supabase)
- [ ] Database credentials obtained
- [ ] Production `DATABASE_URL` configured in `.env`
- [ ] Database tables created in production
- [ ] Data migrated from SQLite to PostgreSQL (if needed)
- [ ] Database connection tested

### 14. Hosting Platform Setup
Choose one platform and complete:

**Option A: Streamlit Community Cloud** (Easiest)
- [ ] Streamlit Community Cloud account created
- [ ] App deployed from GitHub repository
- [ ] Environment variables/secrets configured
- [ ] App URL tested

**Option B: Render.com**
- [ ] Render account created
- [ ] Web service created (Python)
- [ ] Build command configured: `pip install -r requirements.txt`
- [ ] Start command configured: `streamlit run src/dashboard/app.py --server.port=$PORT`
- [ ] Environment variables configured
- [ ] PostgreSQL database connected
- [ ] Custom domain configured (optional)
- [ ] App deployed and tested

**Option C: Railway.app**
- [ ] Railway account created
- [ ] New project created from GitHub
- [ ] Environment variables configured
- [ ] PostgreSQL plugin added
- [ ] App deployed and tested

**Option D: Heroku**
- [ ] Heroku account created
- [ ] `Procfile` created: `web: streamlit run src/dashboard/app.py --server.port=$PORT`
- [ ] Heroku app created: `heroku create smart-money-divergence`
- [ ] PostgreSQL addon added: `heroku addons:create heroku-postgresql:mini`
- [ ] Environment variables set: `heroku config:set KEY=VALUE`
- [ ] App deployed: `git push heroku main`
- [ ] App tested: `heroku open`

### 15. Production Configuration
- [ ] `ENVIRONMENT=production` set in production `.env`
- [ ] `LOG_LEVEL=WARNING` or `ERROR` in production
- [ ] SQL query logging disabled (`SQL_ECHO=false`)
- [ ] Caching enabled for performance
- [ ] Rate limiting properly configured
- [ ] Error tracking setup (Sentry - optional)

### 16. Security Checklist
- [ ] `.env` file never committed to Git
- [ ] API keys and secrets stored securely (environment variables)
- [ ] Database credentials not exposed in code
- [ ] HTTPS enabled on production URL
- [ ] Input validation implemented (ticker symbols, dates)
- [ ] SQL injection prevention (using SQLAlchemy ORM)
- [ ] Rate limiting enforced
- [ ] Error messages don't expose sensitive info

---

## Phase 6: Monitoring & Maintenance

### 17. Testing & Verification
- [ ] Test all 12 tickers load correctly
- [ ] Test date range filtering works
- [ ] Test data toggles function properly
- [ ] Test chart interactivity (zoom, pan, hover)
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Verify loading performance (< 5 seconds)
- [ ] Check for console errors or warnings
- [ ] Verify all tooltips display correctly
- [ ] Test error states (no data, API failures)

### 18. Documentation
- [ ] README.md complete with setup instructions
- [ ] TECHNICAL-SPEC.md updated with implementation details
- [ ] FEATURE-PLAN.md reviewed and accurate
- [ ] API documentation written (if exposing APIs)
- [ ] Deployment guide written
- [ ] Troubleshooting guide created
- [ ] Code comments added where needed

### 19. Monitoring Setup (Optional)
- [ ] Application logging configured
- [ ] Error tracking enabled (Sentry, Rollbar, etc.)
- [ ] Uptime monitoring setup (UptimeRobot, etc.)
- [ ] Database backup strategy configured
- [ ] Performance monitoring enabled
- [ ] Alert notifications configured

### 20. Data Refresh Strategy
- [ ] Manual data refresh process documented
- [ ] Data collection scripts tested
- [ ] Schedule for quarterly 13F updates documented
- [ ] Schedule for daily retail data updates documented
- [ ] Automated data refresh pipeline (Phase 2 - optional)

---

## Phase 7: Launch

### 21. Pre-Launch Checklist
- [ ] All tests passing
- [ ] All 12 tickers have complete data
- [ ] Dashboard loads without errors
- [ ] Documentation is complete
- [ ] GitHub repository is public (if sharing)
- [ ] Production environment is stable
- [ ] Error handling is comprehensive
- [ ] User experience is smooth and intuitive

### 22. Launch
- [ ] Share dashboard URL with initial users
- [ ] Post to portfolio/LinkedIn (optional)
- [ ] Gather user feedback
- [ ] Monitor for errors or issues
- [ ] Document known issues or limitations

### 23. Post-Launch
- [ ] Monitor application logs
- [ ] Track user engagement (page views, interactions)
- [ ] Collect user feedback
- [ ] Fix critical bugs immediately
- [ ] Plan future enhancements (Phase 2 features)

---

## Quick Start Order

If you're just getting started, complete these items first:

1. ✅ Environment setup (Section 1)
2. ✅ Database setup (Section 2)
3. ✅ Configure `.env` file (Section 3)
4. ✅ Test data collectors (Section 4)
5. ✅ Collect initial data (Section 5)
6. ✅ Run dashboard locally (Section 9)
7. ✅ Test dashboard features (Section 10)

**Then** move on to production deployment if needed.

---

## Support & Resources

### Documentation
- Project docs: `docs/` folder
- Technical spec: `docs/TECHNICAL-SPEC.md`
- Feature plan: `docs/FEATURE-PLAN.md`

### Testing
- Run all tests: `pytest`
- Check coverage: `pytest --cov=src tests/`

### Troubleshooting
- Check logs: `logs/` folder
- Review `.env` configuration
- Verify API credentials
- Check database connection
- Review error messages in console

---

## Notes

- **Start Small**: Get it working locally first, then deploy
- **Test Everything**: Don't skip the testing phase
- **Document As You Go**: Update docs when you make changes
- **Backup Data**: Keep backups of your database
- **Monitor Errors**: Set up error tracking early

---

**Last Updated**: 2025-12-27
**Version**: 1.0
