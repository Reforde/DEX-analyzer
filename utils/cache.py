from cachetools import TTLCache
from typing import Any, Optional
import hashlib
import json


def format_price(price: float) -> str:
    """
    Format price with appropriate decimal places based on value.

    Args:
        price: Price value to format

    Returns:
        Formatted price string with $ prefix

    Examples:
        format_price(50000) -> "$50,000.00"
        format_price(100.5) -> "$100.50"
        format_price(1.234) -> "$1.234"
        format_price(0.12345) -> "$0.1235"
        format_price(0.00012345) -> "$0.0001235"
    """
    if price <= 0:
        return "$0.00"

    # For very small prices (< $0.01), show 6 decimals
    if price < 0.01:
        return f"${price:.6f}".rstrip('0').rstrip('.')
    # For small prices (< $1), show 4 decimals
    elif price < 1:
        return f"${price:.4f}"
    # For medium prices (< $100), show 3 decimals
    elif price < 100:
        return f"${price:.3f}"
    # For larger prices, show 2 decimals with comma separator
    else:
        return f"${price:,.2f}"


class SimpleCache:
    """Simple TTL cache wrapper"""

    def __init__(self, maxsize: int = 1000, ttl: int = 30):
        """
        Initialize cache

        Args:
            maxsize: Maximum number of items in cache
            ttl: Time to live in seconds
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        self.cache[key] = value

    def delete(self, key: str) -> None:
        """Delete item from cache"""
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()

    def make_key(self, *args, **kwargs) -> str:
        """
        Create cache key from arguments

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Hashed cache key
        """
        # Convert args and kwargs to string
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)

        # Hash for shorter key
        return hashlib.md5(key_str.encode()).hexdigest()

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self.cache

    def __len__(self) -> int:
        """Get cache size"""
        return len(self.cache)
