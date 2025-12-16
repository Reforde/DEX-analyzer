from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Token:
    """Token data model"""
    id: Optional[int]
    symbol: str
    name: str
    contract_address_eth: Optional[str]
    contract_address_bsc: Optional[str]
    contract_address_polygon: Optional[str]
    decimals: int
    is_tracked: bool
    created_at: datetime

    def __repr__(self):
        return f"Token(symbol={self.symbol}, name={self.name}, tracked={self.is_tracked})"


@dataclass
class TrackedToken:
    """Tracked token with individual threshold"""
    id: Optional[int]
    token_id: int
    threshold_value: float
    threshold_mode: str  # 'percentage' or 'dollar'
    added_at: datetime

    def __repr__(self):
        mode_symbol = '%' if self.threshold_mode == 'percentage' else '$'
        return f"TrackedToken(token_id={self.token_id}, threshold={self.threshold_value}{mode_symbol})"


@dataclass
class TokenMetrics:
    """Real-time token metrics"""
    id: Optional[int]
    token_id: int
    dex: str
    price_usd: float
    volume_24h: Optional[float]
    liquidity_usd: Optional[float]
    volatility_24h: Optional[float]
    timestamp: datetime

    def __repr__(self):
        return f"TokenMetrics(token_id={self.token_id}, dex={self.dex}, price=${self.price_usd:.4f})"


@dataclass
class OHLCVData:
    """OHLCV candlestick data"""
    id: Optional[int]
    token_id: int
    dex: str
    timeframe: str  # '1m', '5m', '15m', '1h'
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    timestamp: datetime

    def __repr__(self):
        return f"OHLCV(token_id={self.token_id}, dex={self.dex}, tf={self.timeframe}, close=${self.close_price:.4f})"


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity data"""
    id: Optional[int]
    token_id: int
    buy_dex: str
    buy_price: float
    sell_dex: str
    sell_price: float
    profit_percent: float
    profit_dollar: float
    timestamp: datetime

    def __repr__(self):
        return (f"ArbitrageOpportunity(token_id={self.token_id}, "
                f"buy={self.buy_dex}@${self.buy_price:.4f}, "
                f"sell={self.sell_dex}@${self.sell_price:.4f}, "
                f"profit={self.profit_percent:.2f}%)")


@dataclass
class UserPreference:
    """User preference setting"""
    id: Optional[int]
    key: str
    value: str

    def __repr__(self):
        return f"UserPreference(key={self.key}, value={self.value})"
