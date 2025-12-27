"""Reddit sentiment data collector"""

import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import praw
from sqlalchemy.exc import IntegrityError
from textblob import TextBlob

from src.database import RedditSentiment, get_session
from src.utils import get_logger

from .base import BaseCollector


class RedditCollector(BaseCollector):
    """Collects sentiment data from Reddit using PRAW"""

    def __init__(self):
        """Initialize Reddit collector with API credentials"""
        super().__init__(rate_limit=60)  # 60 requests per minute
        self.logger = get_logger(__name__)

        # Initialize Reddit API client
        try:
            self.reddit = praw.Reddit(
                client_id=self.settings.REDDIT_CLIENT_ID,
                client_secret=self.settings.REDDIT_CLIENT_SECRET,
                user_agent=self.settings.REDDIT_USER_AGENT,
                check_for_async=False
            )

            # Test authentication
            self.reddit.user.me()
            self.logger.info("Successfully authenticated with Reddit API")

        except Exception as e:
            self.logger.error(f"Failed to authenticate with Reddit API: {e}")
            raise

        # Compile ticker regex pattern (match $AAPL or AAPL)
        self.ticker_pattern = re.compile(r'\$?([A-Z]{1,5})\b')

    def extract_tickers(self, text: str) -> Set[str]:
        """
        Extract ticker symbols from text.

        Args:
            text: Text to search for tickers

        Returns:
            Set of ticker symbols found
        """
        matches = self.ticker_pattern.findall(text.upper())

        # Filter to only whitelisted tickers
        tickers = {
            ticker for ticker in matches
            if ticker in self.settings.WHITELISTED_TICKERS
        }

        return tickers

    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using TextBlob.

        Args:
            text: Text to analyze

        Returns:
            Sentiment score between -1 (negative) and +1 (positive)
        """
        try:
            blob = TextBlob(text)
            # TextBlob polarity ranges from -1 to 1
            return blob.sentiment.polarity
        except Exception as e:
            self.logger.debug(f"Error analyzing sentiment: {e}")
            return 0.0

    def collect_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Collect Reddit sentiment data for a ticker.

        Searches posts and comments in configured subreddits,
        aggregates mentions and sentiment by day.

        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date (defaults to today)

        Returns:
            Number of daily records inserted
        """
        if end_date is None:
            end_date = datetime.now()

        self.logger.info(
            f"Fetching Reddit data for {symbol} from {start_date.date()} to {end_date.date()}"
        )

        # Storage for daily aggregated data
        daily_data: Dict[str, Dict] = defaultdict(
            lambda: {"mentions": 0, "sentiment_scores": []}
        )

        try:
            # Search each subreddit
            for subreddit_name in self.settings.REDDIT_SUBREDDITS:
                if self.rate_limiter:
                    self.rate_limiter.wait_if_needed()

                subreddit = self.reddit.subreddit(subreddit_name.strip())

                # Search for ticker symbol
                search_query = f"{symbol} OR ${symbol}"

                try:
                    # Search posts
                    for submission in subreddit.search(
                        search_query,
                        time_filter='all',
                        limit=self.settings.REDDIT_MAX_POSTS_PER_DAY
                    ):
                        created_date = datetime.fromtimestamp(submission.created_utc)

                        # Skip if outside date range
                        if created_date < start_date or created_date > end_date:
                            continue

                        # Extract tickers from title and body
                        text = f"{submission.title} {submission.selftext}"
                        tickers = self.extract_tickers(text)

                        if symbol in tickers:
                            date_key = created_date.strftime('%Y-%m-%d')
                            daily_data[date_key]["mentions"] += 1

                            # Analyze sentiment
                            sentiment = self.analyze_sentiment(text)
                            daily_data[date_key]["sentiment_scores"].append(sentiment)

                        # Also check comments
                        if self.rate_limiter:
                            self.rate_limiter.wait_if_needed()

                        try:
                            submission.comments.replace_more(limit=0)
                            for comment in submission.comments.list()[:50]:  # Limit comments per post
                                if comment.score >= self.settings.REDDIT_MIN_COMMENT_KARMA:
                                    comment_tickers = self.extract_tickers(comment.body)

                                    if symbol in comment_tickers:
                                        comment_date = datetime.fromtimestamp(comment.created_utc)

                                        if start_date <= comment_date <= end_date:
                                            date_key = comment_date.strftime('%Y-%m-%d')
                                            daily_data[date_key]["mentions"] += 1

                                            sentiment = self.analyze_sentiment(comment.body)
                                            daily_data[date_key]["sentiment_scores"].append(sentiment)

                        except Exception as comment_error:
                            self.logger.debug(f"Error processing comments: {comment_error}")

                except Exception as search_error:
                    self.logger.warning(
                        f"Error searching r/{subreddit_name} for {symbol}: {search_error}"
                    )

            # Insert aggregated daily data into database
            records_inserted = 0

            with get_session() as session:
                ticker_obj = self.get_or_create_ticker(session, symbol)

                for date_str, data in daily_data.items():
                    try:
                        # Calculate average sentiment
                        if data["sentiment_scores"]:
                            avg_sentiment = sum(data["sentiment_scores"]) / len(data["sentiment_scores"])
                        else:
                            avg_sentiment = 0.0

                        sentiment = RedditSentiment(
                            ticker_id=ticker_obj.ticker_id,
                            date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                            mention_count=data["mentions"],
                            sentiment_score=round(avg_sentiment, 2)
                        )
                        session.add(sentiment)
                        records_inserted += 1

                    except IntegrityError:
                        session.rollback()
                        self.logger.debug(
                            f"Reddit sentiment for {symbol} on {date_str} already exists"
                        )
                    except Exception as e:
                        session.rollback()
                        self.logger.error(
                            f"Error inserting sentiment for {symbol} on {date_str}: {e}"
                        )

                session.commit()

            self.logger.info(
                f"Inserted {records_inserted} Reddit sentiment records for {symbol}"
            )
            return records_inserted

        except Exception as e:
            self.logger.error(
                f"Failed to collect Reddit data for {symbol}: {e}",
                exc_info=True
            )
            return 0
