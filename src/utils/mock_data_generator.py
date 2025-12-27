"""Mock data generator for testing dashboard without API access"""

import random
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
from sqlalchemy.exc import IntegrityError

from src.config import get_settings
from src.database import (
    GoogleTrend,
    InsiderTransaction,
    InstitutionalHolding,
    Price,
    RedditSentiment,
    Ticker,
    get_session,
)
from src.utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


class MockDataGenerator:
    """Generates realistic mock data for all three data pillars"""

    def __init__(self, start_date: datetime = None, end_date: datetime = None):
        """
        Initialize mock data generator.

        Args:
            start_date: Start date for mock data (defaults to DATA_START_DATE)
            end_date: End date for mock data (defaults to today)
        """
        self.start_date = start_date or settings.DATA_START_DATE
        self.end_date = end_date or datetime.now()
        self.logger = get_logger(__name__)

        # Generate date range (daily)
        self.dates = self._generate_date_range()

        # Stock-specific parameters for realistic patterns
        self.stock_profiles = self._initialize_stock_profiles()

    def _generate_date_range(self) -> List[datetime]:
        """Generate list of dates from start to end"""
        dates = []
        current = self.start_date
        while current <= self.end_date:
            dates.append(current)
            current += timedelta(days=1)
        return dates

    def _initialize_stock_profiles(self) -> Dict[str, Dict]:
        """
        Define stock-specific characteristics for realistic mock data.

        Each profile includes:
        - volatility: Price volatility multiplier
        - base_price: Starting price
        - trend: Overall trend direction (bullish/bearish/neutral)
        - retail_interest: Retail sentiment intensity (0-1)
        - institutional_interest: Institutional interest level (0-1)
        """
        return {
            # Magnificent 7 - Large Cap Tech
            "AAPL": {
                "volatility": 0.015,
                "base_price": 180.0,
                "trend": "bullish",
                "retail_interest": 0.6,
                "institutional_interest": 0.9,
            },
            "MSFT": {
                "volatility": 0.012,
                "base_price": 370.0,
                "trend": "bullish",
                "retail_interest": 0.5,
                "institutional_interest": 0.95,
            },
            "GOOGL": {
                "volatility": 0.018,
                "base_price": 140.0,
                "trend": "neutral",
                "retail_interest": 0.5,
                "institutional_interest": 0.85,
            },
            "AMZN": {
                "volatility": 0.020,
                "base_price": 150.0,
                "trend": "bullish",
                "retail_interest": 0.6,
                "institutional_interest": 0.9,
            },
            "NVDA": {
                "volatility": 0.035,
                "base_price": 450.0,
                "trend": "bullish",
                "retail_interest": 0.85,
                "institutional_interest": 0.8,
            },
            "META": {
                "volatility": 0.025,
                "base_price": 350.0,
                "trend": "bullish",
                "retail_interest": 0.6,
                "institutional_interest": 0.75,
            },
            "TSLA": {
                "volatility": 0.040,
                "base_price": 240.0,
                "trend": "neutral",
                "retail_interest": 0.95,
                "institutional_interest": 0.6,
            },
            # Hype Stocks - High Retail Interest
            "ASTS": {
                "volatility": 0.060,
                "base_price": 15.0,
                "trend": "bullish",
                "retail_interest": 0.9,
                "institutional_interest": 0.3,
            },
            "MU": {
                "volatility": 0.030,
                "base_price": 90.0,
                "trend": "neutral",
                "retail_interest": 0.6,
                "institutional_interest": 0.7,
            },
            "COIN": {
                "volatility": 0.065,
                "base_price": 150.0,
                "trend": "neutral",
                "retail_interest": 0.85,
                "institutional_interest": 0.4,
            },
            "SMCI": {
                "volatility": 0.055,
                "base_price": 800.0,
                "trend": "bullish",
                "retail_interest": 0.75,
                "institutional_interest": 0.6,
            },
            "HOOD": {
                "volatility": 0.050,
                "base_price": 15.0,
                "trend": "neutral",
                "retail_interest": 0.8,
                "institutional_interest": 0.45,
            },
        }

    def _generate_price_series(self, symbol: str) -> List[Dict]:
        """
        Generate realistic price data with volume.

        Uses geometric Brownian motion for realistic price movements.
        """
        profile = self.stock_profiles[symbol]
        base_price = profile["base_price"]
        volatility = profile["volatility"]
        trend = profile["trend"]

        # Trend drift
        drift = {"bullish": 0.0003, "bearish": -0.0002, "neutral": 0.0}[trend]

        prices = []
        current_price = base_price

        for date in self.dates:
            # Geometric Brownian motion
            returns = drift + volatility * np.random.randn()
            current_price *= 1 + returns

            # Add occasional "news events" (spikes)
            if random.random() < 0.02:  # 2% chance of event
                event_magnitude = random.uniform(-0.05, 0.08)
                current_price *= 1 + event_magnitude

            # Generate OHLCV
            daily_volatility = volatility * current_price
            open_price = current_price + random.gauss(0, daily_volatility * 0.3)
            close_price = current_price + random.gauss(0, daily_volatility * 0.3)
            high_price = max(open_price, close_price) + abs(
                random.gauss(0, daily_volatility * 0.5)
            )
            low_price = min(open_price, close_price) - abs(
                random.gauss(0, daily_volatility * 0.5)
            )

            # Volume correlated with price movement
            base_volume = 10_000_000 * profile["retail_interest"]
            volatility_multiplier = abs(close_price - open_price) / open_price
            volume = int(base_volume * (1 + volatility_multiplier * 5))

            prices.append(
                {
                    "date": date.date(),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume,
                }
            )

        return prices

    def _generate_institutional_holdings(self, symbol: str) -> List[Dict]:
        """
        Generate quarterly institutional holdings (13F data).

        Simulates gradual accumulation or distribution.
        """
        profile = self.stock_profiles[symbol]
        institutional_interest = profile["institutional_interest"]

        # Generate quarterly dates
        quarters = []
        current = self.start_date
        while current <= self.end_date:
            # 13F filed ~45 days after quarter end
            filing_date = current + timedelta(days=45)
            if filing_date <= self.end_date:
                quarters.append(
                    {
                        "quarter_end": current.date(),
                        "filing_date": filing_date.date(),
                    }
                )
            current += timedelta(days=90)

        holdings = []
        base_shares = int(50_000_000 * institutional_interest)
        current_shares = base_shares

        for quarter in quarters:
            # Gradual trend-following behavior
            trend_direction = {
                "bullish": random.uniform(0.02, 0.08),
                "bearish": random.uniform(-0.05, -0.01),
                "neutral": random.uniform(-0.02, 0.02),
            }[profile["trend"]]

            current_shares = int(current_shares * (1 + trend_direction))

            # Number of institutional holders
            num_holders = int(300 * institutional_interest)

            holdings.append(
                {
                    "quarter_end": quarter["quarter_end"],
                    "filing_date": quarter["filing_date"],
                    "shares_held": current_shares,
                    "market_value": current_shares
                    * profile["base_price"]
                    * random.uniform(0.95, 1.05),
                    "ownership_percent": random.uniform(5.0, 25.0),
                }
            )

        return holdings

    def _generate_form4_transactions(self, symbol: str) -> List[Dict]:
        """
        Generate insider transactions (Form 4 data).

        Simulates occasional insider buys/sells.
        """
        profile = self.stock_profiles[symbol]
        transactions = []

        # Insiders trade occasionally (every 2-4 weeks)
        num_transactions = len(self.dates) // random.randint(14, 28)

        for _ in range(num_transactions):
            transaction_date = random.choice(self.dates)
            filing_date = transaction_date + timedelta(days=random.randint(1, 3))

            # Insider type
            insider_types = [
                "CEO",
                "CFO",
                "Director",
                "VP",
                "10% Owner",
                "COO",
                "CTO",
            ]
            insider_title = random.choice(insider_types)

            # Transaction type (insiders usually sell more than buy)
            is_buy = random.random() < 0.3  # 30% buys, 70% sells

            # Shares transacted
            shares = random.randint(5_000, 100_000)

            # Price around current level (approximate)
            price = profile["base_price"] * random.uniform(0.9, 1.1)

            transactions.append(
                {
                    "transaction_date": transaction_date.date(),
                    "shares_traded": shares if is_buy else -shares,
                    "transaction_type": "buy" if is_buy else "sell",
                }
            )

        return sorted(transactions, key=lambda x: x["transaction_date"])

    def _generate_google_trends(self, symbol: str) -> List[Dict]:
        """
        Generate Google Trends search volume data.

        Simulates weekly retail interest with spikes.
        """
        profile = self.stock_profiles[symbol]
        retail_interest = profile["retail_interest"]

        trends = []
        base_volume = int(50 * retail_interest)

        # Generate weekly data
        current = self.start_date
        while current <= self.end_date:
            # Base volume with noise
            volume = base_volume + random.randint(-10, 10)

            # Occasional spikes (earnings, news events)
            if random.random() < 0.05:  # 5% chance of spike
                volume = int(volume * random.uniform(2.0, 5.0))

            # Clamp to 0-100 (Google Trends scale)
            volume = max(0, min(100, volume))

            trends.append({"date": current.date(), "search_interest": volume})

            current += timedelta(days=7)  # Weekly data

        return trends

    def _generate_reddit_sentiment(self, symbol: str) -> List[Dict]:
        """
        Generate Reddit sentiment data.

        Simulates daily mentions and sentiment scores.
        """
        profile = self.stock_profiles[symbol]
        retail_interest = profile["retail_interest"]

        sentiments = []
        base_mentions = int(100 * retail_interest)

        for date in self.dates:
            # Skip weekends (less Reddit activity)
            if date.weekday() >= 5:
                mentions = int(base_mentions * 0.3)
            else:
                mentions = base_mentions + random.randint(-20, 30)

            # Occasional viral posts
            if random.random() < 0.03:  # 3% chance
                mentions = int(mentions * random.uniform(3.0, 10.0))

            # Sentiment score (-1 to +1)
            # Correlate with trend but add noise
            base_sentiment = {
                "bullish": 0.3,
                "bearish": -0.2,
                "neutral": 0.0,
            }[profile["trend"]]

            sentiment_score = base_sentiment + random.gauss(0, 0.3)
            sentiment_score = max(-1.0, min(1.0, sentiment_score))

            sentiments.append(
                {
                    "date": date.date(),
                    "mention_count": mentions,
                    "sentiment_score": round(sentiment_score, 2),
                }
            )

        return sentiments

    def generate_all_mock_data(self) -> None:
        """Generate and insert mock data for all tickers into database"""

        self.logger.info(
            f"Generating mock data from {self.start_date.date()} to {self.end_date.date()}"
        )

        with get_session() as session:
            for symbol in settings.WHITELISTED_TICKERS:
                self.logger.info(f"Generating mock data for {symbol}...")

                # Get or create ticker
                ticker = session.query(Ticker).filter_by(symbol=symbol).first()
                if not ticker:
                    ticker = Ticker(
                        symbol=symbol,
                        company_name=settings.TICKER_COMPANY_MAP.get(
                            symbol, f"{symbol} Corporation"
                        ),
                    )
                    session.add(ticker)
                    session.flush()

                ticker_id = ticker.ticker_id

                # Generate price data
                price_data = self._generate_price_series(symbol)
                for data in price_data:
                    price = Price(ticker_id=ticker_id, **data)
                    session.add(price)
                self.logger.info(f"  ✓ Generated {len(price_data)} price records")

                # Generate institutional holdings
                holdings_data = self._generate_institutional_holdings(symbol)
                for data in holdings_data:
                    holding = InstitutionalHolding(ticker_id=ticker_id, **data)
                    session.add(holding)
                self.logger.info(
                    f"  ✓ Generated {len(holdings_data)} institutional holdings"
                )

                # Generate insider transactions
                insider_data = self._generate_form4_transactions(symbol)
                for data in insider_data:
                    transaction = InsiderTransaction(ticker_id=ticker_id, **data)
                    session.add(transaction)
                self.logger.info(
                    f"  ✓ Generated {len(insider_data)} insider transactions"
                )

                # Generate Google Trends
                trends_data = self._generate_google_trends(symbol)
                for data in trends_data:
                    trend = GoogleTrend(ticker_id=ticker_id, **data)
                    session.add(trend)
                self.logger.info(
                    f"  ✓ Generated {len(trends_data)} Google Trends records"
                )

                # Generate Reddit sentiment
                reddit_data = self._generate_reddit_sentiment(symbol)
                for data in reddit_data:
                    sentiment = RedditSentiment(ticker_id=ticker_id, **data)
                    session.add(sentiment)
                self.logger.info(
                    f"  ✓ Generated {len(reddit_data)} Reddit sentiment records"
                )

                session.commit()

        self.logger.info("✓ Mock data generation complete!")

    def generate_reddit_only(self) -> None:
        """Generate and insert ONLY mock Reddit sentiment data into database"""

        self.logger.info(
            f"Generating mock Reddit data from {self.start_date.date()} to {self.end_date.date()}"
        )

        with get_session() as session:
            for symbol in settings.WHITELISTED_TICKERS:
                self.logger.info(f"Generating mock Reddit data for {symbol}...")

                # Get or create ticker
                ticker = session.query(Ticker).filter_by(symbol=symbol).first()
                if not ticker:
                    ticker = Ticker(
                        symbol=symbol,
                        company_name=settings.TICKER_COMPANY_MAP.get(
                            symbol, f"{symbol} Corporation"
                        ),
                    )
                    session.add(ticker)
                    session.flush()

                ticker_id = ticker.ticker_id

                # Generate Reddit sentiment only
                reddit_data = self._generate_reddit_sentiment(symbol)
                for data in reddit_data:
                    sentiment = RedditSentiment(ticker_id=ticker_id, **data)
                    session.add(sentiment)
                self.logger.info(
                    f"  ✓ Generated {len(reddit_data)} Reddit sentiment records"
                )

                session.commit()

        self.logger.info("✓ Mock Reddit data generation complete!")

    def clear_all_mock_data(self) -> None:
        """Clear all mock data from database (use when switching to real data)"""

        self.logger.warning("Clearing all mock data from database...")

        with get_session() as session:
            session.query(Price).delete()
            session.query(InstitutionalHolding).delete()
            session.query(InsiderTransaction).delete()
            session.query(GoogleTrend).delete()
            session.query(RedditSentiment).delete()
            session.commit()

        self.logger.info("✓ All mock data cleared")


def main():
    """Generate mock data for all tickers"""

    generator = MockDataGenerator()
    generator.generate_all_mock_data()

    print("\n" + "=" * 60)
    print("Mock data generation complete!")
    print("=" * 60)
    print("\nYou can now run the dashboard to visualize the data:")
    print("  streamlit run src/dashboard/app.py")
    print("\nTo clear mock data later (when using real data):")
    print("  from src.utils.mock_data_generator import MockDataGenerator")
    print("  MockDataGenerator().clear_all_mock_data()")
    print()


if __name__ == "__main__":
    main()
