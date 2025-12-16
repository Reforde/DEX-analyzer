"""
Data providers for fetching cryptocurrency prices.
This application uses CoinGecko API exclusively for price data.
"""

from .coingecko_provider import CoinGeckoProvider

__all__ = ['CoinGeckoProvider']
