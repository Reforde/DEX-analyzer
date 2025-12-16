
import sqlite3
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
from config import Config
from database.models import (
    Token, TrackedToken, TokenMetrics, OHLCVData,
    ArbitrageOpportunity, UserPreference
)


class DatabaseManager:
    """Manages SQLite database operations for DEX analyzer"""

    def __init__(self, db_name: str = Config.DATABASE_NAME):
        """
        Initialize database connection

        Args:
            db_name: Name of the SQLite database file
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        """Create necessary database tables if they don't exist"""

        # User preferences table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        ''')

        # Tokens table (40 most popular tokens)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                contract_address_eth TEXT,
                contract_address_bsc TEXT,
                contract_address_polygon TEXT,
                decimals INTEGER DEFAULT 18,
                is_tracked BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tracked tokens with individual thresholds
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                threshold_value REAL NOT NULL,
                threshold_mode TEXT NOT NULL CHECK(threshold_mode IN ('percentage', 'dollar')),
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (token_id) REFERENCES tokens(id) ON DELETE CASCADE,
                UNIQUE(token_id)
            )
        ''')

        # Real-time token metrics
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                dex TEXT NOT NULL,
                price_usd REAL NOT NULL,
                volume_24h REAL,
                liquidity_usd REAL,
                volatility_24h REAL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (token_id) REFERENCES tokens(id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_token_metrics_lookup
            ON token_metrics(token_id, dex, timestamp)
        ''')

        # OHLCV historical data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                dex TEXT NOT NULL,
                timeframe TEXT NOT NULL CHECK(timeframe IN ('1m', '5m', '15m', '1h')),
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (token_id) REFERENCES tokens(id) ON DELETE CASCADE,
                UNIQUE(token_id, dex, timeframe, timestamp)
            )
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ohlcv_lookup
            ON ohlcv_data(token_id, dex, timeframe, timestamp)
        ''')

        # Arbitrage opportunities
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                buy_dex TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_dex TEXT NOT NULL,
                sell_price REAL NOT NULL,
                profit_percent REAL NOT NULL,
                profit_dollar REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (token_id) REFERENCES tokens(id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_arb_time ON arbitrage_opportunities(timestamp)
        ''')

        self.conn.commit()

    # ==================== TOKEN OPERATIONS ====================

    def insert_token(self, symbol: str, name: str, decimals: int = 18,
                     eth_address: Optional[str] = None,
                     bsc_address: Optional[str] = None,
                     polygon_address: Optional[str] = None) -> int:
        """Insert a new token"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO tokens
            (symbol, name, decimals, contract_address_eth, contract_address_bsc, contract_address_polygon)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (symbol, name, decimals, eth_address, bsc_address, polygon_address))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_tokens(self) -> List[Token]:
        """Get all tokens"""
        self.cursor.execute('''
            SELECT id, symbol, name, contract_address_eth, contract_address_bsc,
                   contract_address_polygon, decimals, is_tracked, created_at
            FROM tokens
            ORDER BY symbol
        ''')
        rows = self.cursor.fetchall()
        return [Token(*row) for row in rows]

    def get_token_by_symbol(self, symbol: str) -> Optional[Token]:
        """Get token by symbol"""
        self.cursor.execute('''
            SELECT id, symbol, name, contract_address_eth, contract_address_bsc,
                   contract_address_polygon, decimals, is_tracked, created_at
            FROM tokens
            WHERE symbol = ?
        ''', (symbol,))
        row = self.cursor.fetchone()
        return Token(*row) if row else None

    def get_token_by_id(self, token_id: int) -> Optional[Token]:
        """Get token by ID"""
        self.cursor.execute('''
            SELECT id, symbol, name, contract_address_eth, contract_address_bsc,
                   contract_address_polygon, decimals, is_tracked, created_at
            FROM tokens
            WHERE id = ?
        ''', (token_id,))
        row = self.cursor.fetchone()
        return Token(*row) if row else None

    # ==================== TRACKED TOKENS OPERATIONS ====================

    def add_tracked_token(self, token_id: int, threshold_value: float,
                         threshold_mode: str = 'percentage') -> int:
        """Add token to tracked list with threshold"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO tracked_tokens (token_id, threshold_value, threshold_mode)
            VALUES (?, ?, ?)
        ''', (token_id, threshold_value, threshold_mode))

        # Update is_tracked flag
        self.cursor.execute('UPDATE tokens SET is_tracked = 1 WHERE id = ?', (token_id,))
        self.conn.commit()
        return self.cursor.lastrowid

    def remove_tracked_token(self, token_id: int) -> None:
        """Remove token from tracked list"""
        self.cursor.execute('DELETE FROM tracked_tokens WHERE token_id = ?', (token_id,))
        self.cursor.execute('UPDATE tokens SET is_tracked = 0 WHERE id = ?', (token_id,))
        self.conn.commit()

    def update_token_threshold(self, token_id: int, threshold_value: float,
                               threshold_mode: str) -> None:
        """Update threshold for tracked token"""
        self.cursor.execute('''
            UPDATE tracked_tokens
            SET threshold_value = ?, threshold_mode = ?
            WHERE token_id = ?
        ''', (threshold_value, threshold_mode, token_id))
        self.conn.commit()

    def get_tracked_tokens(self) -> List[Tuple[Token, TrackedToken]]:
        """Get all tracked tokens with their thresholds"""
        self.cursor.execute('''
            SELECT t.id, t.symbol, t.name, t.contract_address_eth, t.contract_address_bsc,
                   t.contract_address_polygon, t.decimals, t.is_tracked, t.created_at,
                   tt.id, tt.token_id, tt.threshold_value, tt.threshold_mode, tt.added_at
            FROM tokens t
            INNER JOIN tracked_tokens tt ON t.id = tt.token_id
            WHERE t.is_tracked = 1
            ORDER BY tt.added_at DESC
        ''')
        rows = self.cursor.fetchall()
        return [(Token(*row[:9]), TrackedToken(*row[9:])) for row in rows]

    def get_available_tokens(self) -> List[Token]:
        """Get tokens that are not tracked"""
        self.cursor.execute('''
            SELECT id, symbol, name, contract_address_eth, contract_address_bsc,
                   contract_address_polygon, decimals, is_tracked, created_at
            FROM tokens
            WHERE is_tracked = 0
            ORDER BY symbol
        ''')
        rows = self.cursor.fetchall()
        return [Token(*row) for row in rows]

    # ==================== TOKEN METRICS OPERATIONS ====================

    def insert_token_metrics(self, token_id: int, dex: str, price_usd: float,
                            volume_24h: Optional[float] = None,
                            liquidity_usd: Optional[float] = None,
                            volatility_24h: Optional[float] = None,
                            timestamp: Optional[datetime] = None) -> int:
        """Insert token metrics"""
        if timestamp is None:
            timestamp = datetime.now()

        self.cursor.execute('''
            INSERT INTO token_metrics
            (token_id, dex, price_usd, volume_24h, liquidity_usd, volatility_24h, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (token_id, dex, price_usd, volume_24h, liquidity_usd, volatility_24h, timestamp))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_latest_token_metrics(self, token_id: int, dex: Optional[str] = None) -> List[TokenMetrics]:
        """Get latest metrics for a token"""
        if dex:
            self.cursor.execute('''
                SELECT id, token_id, dex, price_usd, volume_24h, liquidity_usd, volatility_24h, timestamp
                FROM token_metrics
                WHERE token_id = ? AND dex = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (token_id, dex))
        else:
            # Get latest for each DEX
            self.cursor.execute('''
                SELECT tm.id, tm.token_id, tm.dex, tm.price_usd, tm.volume_24h,
                       tm.liquidity_usd, tm.volatility_24h, tm.timestamp
                FROM token_metrics tm
                INNER JOIN (
                    SELECT dex, MAX(timestamp) as max_time
                    FROM token_metrics
                    WHERE token_id = ?
                    GROUP BY dex
                ) latest ON tm.dex = latest.dex AND tm.timestamp = latest.max_time
                WHERE tm.token_id = ?
            ''', (token_id, token_id))

        rows = self.cursor.fetchall()
        return [TokenMetrics(*row) for row in rows]

    # ==================== OHLCV OPERATIONS ====================

    def insert_ohlcv(self, token_id: int, dex: str, timeframe: str,
                     open_price: float, high_price: float, low_price: float,
                     close_price: float, volume: float, timestamp: datetime) -> None:
        """Insert OHLCV data"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO ohlcv_data
            (token_id, dex, timeframe, open_price, high_price, low_price, close_price, volume, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (token_id, dex, timeframe, open_price, high_price, low_price, close_price, volume, timestamp))
        self.conn.commit()

    def get_ohlcv_data(self, token_id: int, dex: str, timeframe: str,
                       hours: int = 24) -> List[OHLCVData]:
        """Get OHLCV data for specified period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.cursor.execute('''
            SELECT id, token_id, dex, timeframe, open_price, high_price, low_price,
                   close_price, volume, timestamp
            FROM ohlcv_data
            WHERE token_id = ? AND dex = ? AND timeframe = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (token_id, dex, timeframe, cutoff_time))
        rows = self.cursor.fetchall()
        return [OHLCVData(*row) for row in rows]

    def cleanup_old_ohlcv(self, hours: int = 24) -> int:
        """Delete OHLCV data older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.cursor.execute('DELETE FROM ohlcv_data WHERE timestamp < ?', (cutoff_time,))
        self.conn.commit()
        return self.cursor.rowcount

    # ==================== ARBITRAGE OPPORTUNITIES ====================

    def insert_arbitrage_opportunity(self, token_id: int, buy_dex: str, buy_price: float,
                                    sell_dex: str, sell_price: float,
                                    profit_percent: float, profit_dollar: float,
                                    timestamp: Optional[datetime] = None) -> int:
        """Insert arbitrage opportunity"""
        if timestamp is None:
            timestamp = datetime.now()

        self.cursor.execute('''
            INSERT INTO arbitrage_opportunities
            (token_id, buy_dex, buy_price, sell_dex, sell_price, profit_percent, profit_dollar, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (token_id, buy_dex, buy_price, sell_dex, sell_price, profit_percent, profit_dollar, timestamp))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_latest_arbitrage_opportunities(self) -> List[Tuple]:
        """Get the most recent arbitrage opportunities with token info"""
        self.cursor.execute('''
            SELECT t.symbol, a.buy_dex, a.buy_price, a.sell_dex, a.sell_price,
                   a.profit_percent, a.profit_dollar, a.timestamp
            FROM arbitrage_opportunities a
            INNER JOIN tokens t ON a.token_id = t.id
            WHERE a.timestamp = (SELECT MAX(timestamp) FROM arbitrage_opportunities)
            ORDER BY a.profit_percent DESC
        ''')
        return self.cursor.fetchall()

    # ==================== USER PREFERENCES ====================

    def set_preference(self, key: str, value: str) -> None:
        """Set user preference"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (key, value)
            VALUES (?, ?)
        ''', (key, value))
        self.conn.commit()

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get user preference"""
        self.cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    # ==================== UTILITY METHODS ====================

    def clear_all_data(self) -> None:
        """Clear all data from the database (keep tokens)"""
        self.cursor.execute("DELETE FROM token_metrics")
        self.cursor.execute("DELETE FROM ohlcv_data")
        self.cursor.execute("DELETE FROM arbitrage_opportunities")
        self.cursor.execute("DELETE FROM tracked_tokens")
        self.cursor.execute("UPDATE tokens SET is_tracked = 0")
        self.conn.commit()

    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}

        tables = ['tokens', 'tracked_tokens', 'token_metrics', 'ohlcv_data', 'arbitrage_opportunities']
        for table in tables:
            self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[table] = self.cursor.fetchone()[0]

        return stats

    def close(self) -> None:
        """Close the database connection"""
        self.conn.close()
