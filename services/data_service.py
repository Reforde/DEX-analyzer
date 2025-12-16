"""
Data Service - CoinGecko-based cryptocurrency data service.

This service uses CoinGecko API for real cryptocurrency prices
and simulates DEX-specific price variations for arbitrage detection.
"""

from typing import Optional, Dict
from datetime import datetime
from api.data_providers.coingecko_provider import CoinGeckoProvider
from utils.cache import SimpleCache
from config import Config
import random


class DataService:
    """
    Unified service for fetching cryptocurrency data
    Uses CoinGecko for base prices and simulates DEX price variations
    """

    def __init__(self):
        """Initialize data service"""
        self.coingecko = CoinGeckoProvider()
        self.price_cache = SimpleCache(maxsize=1000, ttl=Config.PRICE_CACHE_TTL)

    def get_token_price(self, token_symbol: str, dex_key: str, network: str = "ethereum") -> Optional[Dict]:
        """
        Get current price for a token on a specific DEX

        Args:
            token_symbol: Token symbol (e.g., "ETH", "WBTC")
            dex_key: DEX key from config (e.g., "uniswap_v3")
            network: Network name (ethereum, bsc, polygon)

        Returns:
            Dict with price data or None if failed
        """
        # Create cache key
        cache_key = self.price_cache.make_key(token_symbol, dex_key)

        # Check cache first
        cached = self.price_cache.get(cache_key)
        if cached is not None:
            return cached

        # Get base price from CoinGecko
        base_data = self.coingecko.get_token_price(token_symbol)

        if not base_data:
            return None

        # Generate DEX-specific price data
        result = self._generate_dex_price(base_data, dex_key)

        # Cache the result
        self.price_cache.set(cache_key, result)

        return result

    def _generate_dex_price(self, base_data: Dict, dex_key: str) -> Dict:
        """
        Generate DEX-specific price with simulated variation.

        Args:
            base_data: Base price data from CoinGecko
            dex_key: DEX key for variation seed

        Returns:
            Dict with DEX-specific price data
        """
        # Simulate DEX-specific price variations (0.1-2% difference)
        # In reality, different DEXes have slightly different prices due to liquidity, slippage, etc.
        variation = random.uniform(0.999, 1.02)  # -0.1% to +2%
        dex_price = base_data["price_usd"] * variation

        return {
            "price_usd": round(dex_price, 6),
            "volume_24h": base_data.get("volume_24h", 0),
            "price_change_24h": base_data.get("price_change_24h", 0),
            "liquidity_usd": base_data.get("market_cap", 0) * 0.01,  # Estimate ~1% of market cap
            "last_updated": base_data.get("last_updated"),
            "source": f"{dex_key}_simulated"
        }

    def get_all_dex_prices(self, token_symbol: str) -> Dict[str, Optional[Dict]]:
        """
        Get prices for a token from all available DEXes

        Args:
            token_symbol: Token symbol

        Returns:
            Dict mapping DEX keys to price data
        """
        results = {}

        for dex_key in Config.DEX_CONFIG.keys():
            price_data = self.get_token_price(token_symbol, dex_key)
            if price_data:
                results[dex_key] = price_data

        return results

    def get_bulk_prices_all_dexes(self, token_symbols: list, dex_keys: list = None) -> Dict[str, Dict[str, Dict]]:
        """
        OPTIMIZED: Get prices for multiple tokens across multiple DEXes with a single API call.

        This method fetches all tokens at once from CoinGecko (1 API call),
        then simulates DEX-specific variations for each token-DEX combination.

        Args:
            token_symbols: List of token symbols to fetch
            dex_keys: List of DEX keys (default: all 4 DEXes)

        Returns:
            Nested dict: {symbol: {dex_key: price_data}}

        Example:
            result = {
                'ETH': {
                    'uniswap_v3': {'price_usd': 3500.25, ...},
                    'sushiswap': {'price_usd': 3502.10, ...},
                    ...
                },
                'WBTC': {...}
            }
        """
        if not token_symbols:
            return {}

        if dex_keys is None:
            dex_keys = list(Config.DEX_CONFIG.keys())

        # Step 1: Check cache for all combinations
        cache_hits = {}
        cache_misses = []

        for symbol in token_symbols:
            cache_hits[symbol] = {}
            for dex_key in dex_keys:
                cache_key = self.price_cache.make_key(symbol, dex_key)
                cached = self.price_cache.get(cache_key)

                if cached is not None:
                    # Cache hit
                    cache_hits[symbol][dex_key] = cached
                else:
                    # Cache miss - need to fetch
                    if symbol not in cache_misses:
                        cache_misses.append(symbol)

        # Step 2: Bulk fetch only missing tokens (1 API CALL for all!)
        if cache_misses:
            base_prices = self.coingecko.get_multiple_prices(cache_misses)

            # Step 3: Generate DEX variations for all fetched tokens
            for symbol, base_data in base_prices.items():
                if symbol not in cache_hits:
                    cache_hits[symbol] = {}

                for dex_key in dex_keys:
                    # Generate DEX-specific price
                    dex_price_data = self._generate_dex_price(base_data, dex_key)

                    # Cache it
                    cache_key = self.price_cache.make_key(symbol, dex_key)
                    self.price_cache.set(cache_key, dex_price_data)

                    # Add to results
                    cache_hits[symbol][dex_key] = dex_price_data

        # Step 4: Return all data (from cache + newly fetched)
        return cache_hits

    def get_multiple_token_prices(self, token_symbols: list) -> Dict[str, Dict]:
        """
        Get prices for multiple tokens efficiently

        Args:
            token_symbols: List of token symbols

        Returns:
            Dict mapping symbol to price data (aggregated from all DEXes)
        """
        # Bulk fetch from CoinGecko
        base_prices = self.coingecko.get_multiple_prices(token_symbols)

        result = {}

        for symbol, base_data in base_prices.items():
            if base_data:
                result[symbol] = {
                    "price_usd": base_data["price_usd"],
                    "volume_24h": base_data.get("volume_24h", 0),
                    "price_change_24h": base_data.get("price_change_24h", 0),
                    "market_cap": base_data.get("market_cap", 0),
                    "last_updated": base_data.get("last_updated"),
                    "source": "coingecko"
                }

        return result

    def calculate_volatility(self, price_change_24h: float) -> str:
        """
        Calculate volatility category from 24h price change

        Args:
            price_change_24h: Price change percentage in last 24h

        Returns:
            Volatility category: "Low", "Medium", "High", "Very High"
        """
        abs_change = abs(price_change_24h)

        if abs_change < 2:
            return "Low"
        elif abs_change < 5:
            return "Medium"
        elif abs_change < 10:
            return "High"
        else:
            return "Very High"

    def clear_cache(self) -> None:
        """Clear all caches"""
        self.price_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "price_cache_size": len(self.price_cache.cache)
        }
