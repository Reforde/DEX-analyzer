
from typing import Dict, List, Optional
from datetime import datetime
from database.database_manager import DatabaseManager
from config import Config


class ArbitrageOpportunity:
    """Data class representing an arbitrage opportunity"""
    
    def __init__(self, token: str, buy_dex: str, buy_price: float,
                 sell_dex: str, sell_price: float, profit_percent: float):
        self.token = token
        self.buy_dex = buy_dex
        self.buy_price = buy_price
        self.sell_dex = sell_dex
        self.sell_price = sell_price
        self.profit_percent = profit_percent
    
    def __repr__(self):
        return (f"ArbitrageOpportunity(token={self.token}, "
                f"buy={self.buy_dex}@${self.buy_price:.4f}, "
                f"sell={self.sell_dex}@${self.sell_price:.4f}, "
                f"profit={self.profit_percent:.2f}%)")


class ArbitrageAnalyzer:
    """Analyzes price data to find arbitrage opportunities"""
    
    def __init__(self, db_manager: DatabaseManager, threshold: float = Config.DEFAULT_THRESHOLD):
        """
        Initialize arbitrage analyzer
        
        Args:
            db_manager: Database manager instance
            threshold: Minimum profit percentage to consider as opportunity
        """
        self.db_manager = db_manager
        self.threshold = threshold
    
    def find_opportunities(self, timestamp: datetime, tokens: List[str], 
                          dexes: List[str]) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities by comparing prices across DEXes
        
        Args:
            timestamp: Timestamp of the price data
            tokens: List of token symbols to analyze
            dexes: List of DEX names to compare
            
        Returns:
            List of ArbitrageOpportunity objects
        """
        opportunities = []
        
        for token in tokens:
            prices = {}
            
            # Get latest price for each DEX
            for dex in dexes:
                price = self.db_manager.get_price_for_token(token, dex, timestamp)
                if price and price > 0:
                    prices[dex] = price
            
            # Find arbitrage opportunities
            if len(prices) >= 2:
                opportunity = self._analyze_price_spread(token, prices)
                if opportunity:
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _analyze_price_spread(self, token: str, 
                             prices: Dict[str, float]) -> Optional[ArbitrageOpportunity]:
        """
        Analyze price spread for a token across DEXes
        
        Args:
            token: Token symbol
            prices: Dictionary of {dex: price}
            
        Returns:
            ArbitrageOpportunity if profitable, None otherwise
        """
        min_dex = min(prices, key=prices.get)
        max_dex = max(prices, key=prices.get)
        min_price = prices[min_dex]
        max_price = prices[max_dex]
        
        profit_percent = ((max_price - min_price) / min_price) * 100
        
        if profit_percent >= self.threshold:
            print(f"💰 Arbitrage opportunity: Buy {token} on {min_dex} at ${min_price:.4f}, "
                  f"sell on {max_dex} at ${max_price:.4f} = {profit_percent:.2f}% profit")
            
            return ArbitrageOpportunity(
                token=token,
                buy_dex=min_dex,
                buy_price=min_price,
                sell_dex=max_dex,
                sell_price=max_price,
                profit_percent=profit_percent
            )
        
        return None
    
    def save_opportunities(self, opportunities: List[ArbitrageOpportunity], 
                          timestamp: datetime) -> None:
        """
        Save arbitrage opportunities to database
        
        Args:
            opportunities: List of opportunities to save
            timestamp: Timestamp of the opportunities
        """
        for opp in opportunities:
            self.db_manager.insert_arbitrage_opportunity(
                timestamp=timestamp,
                token=opp.token,
                buy_dex=opp.buy_dex,
                buy_price=opp.buy_price,
                sell_dex=opp.sell_dex,
                sell_price=opp.sell_price,
                profit_percent=opp.profit_percent
            )