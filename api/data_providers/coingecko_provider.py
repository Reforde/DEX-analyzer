"""
CoinGecko API Provider
Provides real cryptocurrency prices from CoinGecko (free tier)
"""

import requests
import time
from typing import Optional, Dict
from datetime import datetime
from config import Config


class CoinGeckoProvider:
    """Provider for fetching data from CoinGecko API"""

    # Token symbol to CoinGecko ID mapping
    SYMBOL_TO_ID = {
        "WBTC": "wrapped-bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "USDC": "usd-coin",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "ADA": "cardano",
        "SOL": "solana",
        "DOGE": "dogecoin",
        "MATIC": "matic-network",
        "DOT": "polkadot",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "ATOM": "cosmos",
        "LTC": "litecoin",
        "ETC": "ethereum-classic",
        "XLM": "stellar",
        "BCH": "bitcoin-cash",
        "ALGO": "algorand",
        "SHIB": "shiba-inu",
        "TRX": "tron",
        "LEO": "leo-token",
        "FTT": "ftx-token",
        "CRO": "crypto-com-chain",
        "NEAR": "near",
        "APE": "apecoin",
        "MANA": "decentraland",
        "SAND": "the-sandbox",
        "AXS": "axie-infinity",
        "EOS": "eos",
        "AAVE": "aave",
        "MKR": "maker",
        "SNX": "havven",
        "GRT": "the-graph",
        "FTM": "fantom",
        "RUNE": "thorchain",
        "LRC": "loopring",
        "1INCH": "1inch",
        "ENJ": "enjincoin"
    }

    def __init__(self):
        """Initialize CoinGecko provider"""
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 10  # seconds
        self.rate_limit_delay = 1.5  # seconds between requests to avoid 429 errors

    def get_token_price(self, token_symbol: str) -> Optional[Dict]:
        """
        Get current token price from CoinGecko

        Args:
            token_symbol: Token symbol (e.g., "ETH", "WBTC")

        Returns:
            Dict with price data or None if failed
        """
        # Get CoinGecko ID
        coin_id = self.SYMBOL_TO_ID.get(token_symbol)
        if not coin_id:
            print(f"Warning: No CoinGecko ID mapping for {token_symbol}")
            return None

        # API endpoint
        endpoint = f"{self.base_url}/simple/price"

        # Parameters
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_market_cap": "true"
        }

        try:
            response = requests.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()

                if coin_id in data:
                    coin_data = data[coin_id]

                    return {
                        "price_usd": coin_data.get("usd", 0),
                        "volume_24h": coin_data.get("usd_24h_vol", 0),
                        "price_change_24h": coin_data.get("usd_24h_change", 0),
                        "market_cap": coin_data.get("usd_market_cap", 0),
                        "last_updated": datetime.now().isoformat(),
                        "source": "coingecko"
                    }

            elif response.status_code == 429:
                print(f"CoinGecko rate limit exceeded. Waiting {self.rate_limit_delay * 2}s...")
                time.sleep(self.rate_limit_delay * 2)
                return None
            else:
                print(f"CoinGecko API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching price from CoinGecko: {str(e)}")
            return None
        finally:
            # Add delay to avoid rate limiting
            time.sleep(self.rate_limit_delay)

    def get_multiple_prices(self, token_symbols: list) -> Dict[str, Optional[Dict]]:
        """
        Get prices for multiple tokens at once (more efficient)

        Args:
            token_symbols: List of token symbols

        Returns:
            Dict mapping symbol to price data
        """
        # Get all CoinGecko IDs
        coin_ids = []
        symbol_to_id = {}

        for symbol in token_symbols:
            coin_id = self.SYMBOL_TO_ID.get(symbol)
            if coin_id:
                coin_ids.append(coin_id)
                symbol_to_id[coin_id] = symbol

        if not coin_ids:
            return {}

        # API endpoint
        endpoint = f"{self.base_url}/simple/price"

        # Parameters - join all IDs
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_market_cap": "true"
        }

        try:
            response = requests.get(
                endpoint,
                params=params,
                timeout=self.timeout * 2  # More time for bulk request
            )

            if response.status_code == 200:
                data = response.json()
                result = {}

                for coin_id, coin_data in data.items():
                    symbol = symbol_to_id[coin_id]
                    result[symbol] = {
                        "price_usd": coin_data.get("usd", 0),
                        "volume_24h": coin_data.get("usd_24h_vol", 0),
                        "price_change_24h": coin_data.get("usd_24h_change", 0),
                        "market_cap": coin_data.get("usd_market_cap", 0),
                        "last_updated": datetime.now().isoformat(),
                        "source": "coingecko"
                    }

                return result

            elif response.status_code == 429:
                print(f"CoinGecko rate limit exceeded. Waiting {self.rate_limit_delay * 2}s...")
                time.sleep(self.rate_limit_delay * 2)
                return {}
            else:
                print(f"CoinGecko API error: {response.status_code}")
                return {}

        except Exception as e:
            print(f"Error fetching prices from CoinGecko: {str(e)}")
            return {}
        finally:
            # Add delay to avoid rate limiting
            time.sleep(self.rate_limit_delay)
