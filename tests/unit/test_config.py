"""Unit tests for configuration module"""

import os
from datetime import datetime

import pytest

from src.config import Settings, get_settings


class TestSettings:
    """Test Settings class"""

    def test_settings_loads_defaults(self):
        """Test that settings loads with default values"""
        settings = Settings()

        assert settings.ENVIRONMENT in ['development', 'production']
        assert settings.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert settings.DATA_START_DATE.year == 2024
        assert settings.DATA_START_DATE.month == 1
        assert settings.DATA_START_DATE.day == 1

    def test_whitelisted_tickers(self):
        """Test that all expected tickers are whitelisted"""
        settings = Settings()

        expected_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'ASTS', 'MU', 'COIN', 'SMCI', 'HOOD'
        ]

        for ticker in expected_tickers:
            assert ticker in settings.WHITELISTED_TICKERS

        assert len(settings.WHITELISTED_TICKERS) == 12

    def test_ticker_company_map(self):
        """Test that ticker-to-company mapping exists"""
        settings = Settings()

        assert settings.TICKER_COMPANY_MAP['AAPL'] == 'Apple Inc.'
        assert settings.TICKER_COMPANY_MAP['MSFT'] == 'Microsoft Corporation'
        assert 'GOOGL' in settings.TICKER_COMPANY_MAP

    def test_database_type_detection_sqlite(self):
        """Test SQLite database detection"""
        settings = Settings()

        # Temporarily set to SQLite
        original_url = settings.DATABASE_URL
        settings.DATABASE_URL = "sqlite:///data/test.db"

        assert settings.database_is_sqlite is True
        assert settings.database_is_postgresql is False

        settings.DATABASE_URL = original_url

    def test_database_type_detection_postgresql(self):
        """Test PostgreSQL database detection"""
        settings = Settings()

        # Temporarily set to PostgreSQL
        original_url = settings.DATABASE_URL
        settings.DATABASE_URL = "postgresql://user:pass@localhost/db"

        assert settings.database_is_sqlite is False
        assert settings.database_is_postgresql is True

        settings.DATABASE_URL = original_url

    def test_environment_checks(self):
        """Test environment detection"""
        settings = Settings()

        original_env = settings.ENVIRONMENT

        settings.ENVIRONMENT = "development"
        assert settings.is_development is True
        assert settings.is_production is False

        settings.ENVIRONMENT = "production"
        assert settings.is_development is False
        assert settings.is_production is True

        settings.ENVIRONMENT = original_env

    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance"""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2


class TestSettingsValidation:
    """Test settings validation"""

    def test_validation_fails_without_reddit_credentials(self, monkeypatch):
        """Test that validation fails with missing Reddit credentials"""
        monkeypatch.setenv("REDDIT_CLIENT_ID", "your_reddit_client_id_here")
        monkeypatch.setenv("REDDIT_CLIENT_SECRET", "your_reddit_client_secret_here")

        settings = Settings()

        with pytest.raises(ValueError, match="Configuration validation failed"):
            settings.validate()

    def test_validation_succeeds_with_valid_credentials(self, monkeypatch):
        """Test that validation passes with valid credentials"""
        # Must set env vars before importing/creating Settings
        import os
        monkeypatch.setattr(os, "environ", {
            **os.environ,
            "REDDIT_CLIENT_ID": "valid_client_id",
            "REDDIT_CLIENT_SECRET": "valid_client_secret",
            "DATABASE_URL": "sqlite:///test.db"
        })

        # Force reload of environment variables
        from importlib import reload
        from src.config import settings as settings_module
        reload(settings_module)

        # Create new settings instance with updated env
        settings = settings_module.Settings()

        # Should not raise
        try:
            settings.validate()
        except ValueError as e:
            pytest.fail(f"Validation should pass with valid credentials: {e}")
