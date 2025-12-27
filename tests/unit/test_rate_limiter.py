"""Unit tests for rate limiter"""

import time

import pytest

from src.utils import RateLimiter


class TestRateLimiter:
    """Test RateLimiter class"""

    def test_rate_limiter_allows_calls_within_limit(self):
        """Test that calls within limit proceed immediately"""
        limiter = RateLimiter(max_calls=5, period=1)

        start_time = time.time()

        # Make 5 calls (should be instant)
        for _ in range(5):
            limiter.wait_if_needed()

        elapsed = time.time() - start_time

        # Should complete almost instantly (allow 0.1s overhead)
        assert elapsed < 0.2

    def test_rate_limiter_blocks_when_exceeded(self):
        """Test that exceeding limit causes blocking"""
        limiter = RateLimiter(max_calls=3, period=1)

        start_time = time.time()

        # Make 3 calls (should be instant)
        for _ in range(3):
            limiter.wait_if_needed()

        # 4th call should block for ~1 second
        limiter.wait_if_needed()

        elapsed = time.time() - start_time

        # Should have waited at least 1 second
        assert elapsed >= 0.9

    def test_rate_limiter_context_manager(self):
        """Test rate limiter as context manager"""
        limiter = RateLimiter(max_calls=2, period=1)

        start_time = time.time()

        # Use as context manager
        with limiter:
            pass

        with limiter:
            pass

        # Third call should block
        with limiter:
            pass

        elapsed = time.time() - start_time

        assert elapsed >= 0.9

    def test_rate_limiter_sliding_window(self):
        """Test that rate limiter uses sliding window"""
        limiter = RateLimiter(max_calls=2, period=1)

        # First call at t=0
        limiter.wait_if_needed()

        # Wait 0.6 seconds
        time.sleep(0.6)

        # Second call at t=0.6
        limiter.wait_if_needed()

        # Third call should only wait ~0.4 seconds (until first call expires)
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should wait between 0.3 and 0.6 seconds
        assert 0.3 <= elapsed <= 0.7
