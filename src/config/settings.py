"""Application settings and configuration management"""

import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application configuration settings loaded from environment variables"""

    # Project paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/divergence.db")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Data collection settings
    DATA_START_DATE: datetime = datetime.strptime(
        os.getenv("DATA_START_DATE", "2024-01-01"),
        "%Y-%m-%d"
    )
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_EXPIRY_HOURS: int = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))

    # API Rate limits (requests per minute)
    SEC_RATE_LIMIT: int = int(os.getenv("SEC_RATE_LIMIT", "60"))
    REDDIT_RATE_LIMIT: int = int(os.getenv("REDDIT_RATE_LIMIT", "60"))
    GOOGLE_TRENDS_RATE_LIMIT: int = int(os.getenv("GOOGLE_TRENDS_RATE_LIMIT", "100"))
    YAHOO_FINANCE_RATE_LIMIT: int = int(os.getenv("YAHOO_FINANCE_RATE_LIMIT", "2000"))

    # Reddit API credentials
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "SmartMoneyDivergence/1.0")

    # Reddit scraping configuration
    REDDIT_SUBREDDITS: List[str] = os.getenv(
        "REDDIT_SUBREDDITS",
        "wallstreetbets,stocks,investing"
    ).split(",")
    REDDIT_MAX_POSTS_PER_DAY: int = int(os.getenv("REDDIT_MAX_POSTS_PER_DAY", "1000"))
    REDDIT_MIN_COMMENT_KARMA: int = int(os.getenv("REDDIT_MIN_COMMENT_KARMA", "5"))

    # Data processing settings
    ZSCORE_SHORT_WINDOW: int = int(os.getenv("ZSCORE_SHORT_WINDOW", "30"))
    ZSCORE_LONG_WINDOW: int = int(os.getenv("ZSCORE_LONG_WINDOW", "90"))
    MIN_DATA_POINTS_FOR_ZSCORE: int = int(os.getenv("MIN_DATA_POINTS_FOR_ZSCORE", "14"))
    MAX_FORWARD_FILL_DAYS: int = int(os.getenv("MAX_FORWARD_FILL_DAYS", "3"))
    IQR_MULTIPLIER: float = float(os.getenv("IQR_MULTIPLIER", "1.5"))
    WINSORIZE_PERCENTILE: int = int(os.getenv("WINSORIZE_PERCENTILE", "99"))

    # Whitelisted tickers (The Magnificent 7 + Hype Stocks)
    WHITELISTED_TICKERS: List[str] = [
        # Magnificent 7
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        # Hype Stocks
        "ASTS", "MU", "COIN", "SMCI", "HOOD"
    ]

    # Ticker company name mapping
    TICKER_COMPANY_MAP: dict = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc. (Google)",
        "AMZN": "Amazon.com Inc.",
        "NVDA": "NVIDIA Corporation",
        "META": "Meta Platforms Inc. (Facebook)",
        "TSLA": "Tesla Inc.",
        "ASTS": "AST SpaceMobile Inc.",
        "MU": "Micron Technology Inc.",
        "COIN": "Coinbase Global Inc.",
        "SMCI": "Super Micro Computer Inc.",
        "HOOD": "Robinhood Markets Inc."
    }

    # Dashboard settings
    DASHBOARD_TITLE: str = os.getenv("DASHBOARD_TITLE", "Smart Money Divergence Index")
    CHART_HEIGHT: int = int(os.getenv("CHART_HEIGHT", "600"))
    CHART_COLOR_INSTITUTIONAL: str = os.getenv("CHART_COLOR_INSTITUTIONAL", "#3B82F6")
    CHART_COLOR_RETAIL: str = os.getenv("CHART_COLOR_RETAIL", "#10B981")
    CHART_COLOR_PRICE: str = os.getenv("CHART_COLOR_PRICE", "#F59E0B")

    def __init__(self):
        """Initialize settings and create necessary directories"""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"

    @property
    def database_is_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def database_is_postgresql(self) -> bool:
        """Check if using PostgreSQL database"""
        return self.DATABASE_URL.startswith("postgresql")

    def validate(self) -> None:
        """Validate critical settings"""
        errors = []

        # Validate Reddit credentials if needed
        if not self.REDDIT_CLIENT_ID or self.REDDIT_CLIENT_ID == "your_reddit_client_id_here":
            errors.append("REDDIT_CLIENT_ID is not set in .env file")

        if not self.REDDIT_CLIENT_SECRET or self.REDDIT_CLIENT_SECRET == "your_reddit_client_secret_here":
            errors.append("REDDIT_CLIENT_SECRET is not set in .env file")

        # Validate database URL
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is not set")

        if errors:
            error_msg = "\n".join(f"  - {err}" for err in errors)
            raise ValueError(f"Configuration validation failed:\n{error_msg}")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    return settings
