
import time
from typing import Optional, Dict
from datetime import datetime
from config import Config
from api.bitquery_client import BitqueryClient


class PriceFetcher:
    """Handles fetching prices from multiple DEXes"""
    
    def __init__(self, api_client: BitqueryClient):
        """
        Initialize price fetcher
        
        Args:
            api_client: Bitquery API client instance
        """
        self.api_client = api_client
        self.config = Config
    
    def get_token_address(self, network: str, token: str) -> Optional[str]:
        """
        Get token contract address for a given network
        
        Args:
            network: Network name (eth or bsc)
            token: Token symbol
            
        Returns:
            Token contract address or None
        """
        network_key = "ethereum" if network == "eth" else "bsc"
        return self.config.TOKEN_ADDRESSES.get(network_key, {}).get(token)
    
    def fetch_price(self, dex: str, token: str, base_currency: str) -> Optional[Dict[str, float]]:
        """
        Fetch price for a token on a specific DEX
        
        Args:
            dex: DEX name
            token: Token symbol
            base_currency: Base currency symbol
            
        Returns:
            Dictionary with 'price' and 'volume' or None if failed
        """
        # Get network for the DEX
        network = self.config.NETWORK_MAPPING.get(dex, "eth")
        
        # Get token addresses
        token_address = self.get_token_address(network, token)
        base_address = self.get_token_address(network, base_currency)
        
        if not token_address or not base_address:
            print(f"Token address not found for {token}/{base_currency} on {network}")
            return None
        
        print(f"Fetching {dex} {token}...")
        
        # Fetch from API
        result = self.api_client.get_token_price(network, token_address, base_address)
        
        if result:
            print(f"✓ Fetched {dex} {token}: ${result['price']:.4f}")
        else:
            print(f"✗ Failed to fetch {dex} {token}")
        
        return result
    
    def fetch_all_prices(self, dexes: list, tokens: list, 
                        base_currency: str) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Fetch prices for all DEX-token combinations
        
        Args:
            dexes: List of DEX names
            tokens: List of token symbols
            base_currency: Base currency symbol
            
        Returns:
            Nested dictionary: {dex: {token: {price, volume}}}
        """
        results = {}
        
        for dex in dexes:
            results[dex] = {}
            for token in tokens:
                price_data = self.fetch_price(dex, token, base_currency)
                if price_data:
                    results[dex][token] = price_data
                
                # Add delay to avoid rate limiting
                time.sleep(self.config.REQUEST_DELAY)
        
        return results