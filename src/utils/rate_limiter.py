"""Rate limiting utility for API calls"""

import time
from collections import deque
from threading import Lock
from typing import Deque


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.

    Ensures API calls don't exceed specified requests per minute.
    """

    def __init__(self, max_calls: int, period: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds (default: 60 for per-minute limiting)
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: Deque[float] = deque()
        self.lock = Lock()

    def wait_if_needed(self) -> None:
        """
        Block if rate limit would be exceeded.

        Automatically waits until a call can be made within the rate limit.
        """
        with self.lock:
            now = time.time()

            # Remove calls outside the time window
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()

            # If at limit, wait until oldest call expires
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0]) + 0.1  # Small buffer
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Clean up expired calls after waiting
                now = time.time()
                while self.calls and self.calls[0] < now - self.period:
                    self.calls.popleft()

            # Record this call
            self.calls.append(time.time())

    def __enter__(self):
        """Context manager entry"""
        self.wait_if_needed()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
