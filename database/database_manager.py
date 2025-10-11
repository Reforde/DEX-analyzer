
import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime
from config import Config


class DatabaseManager:
    """Manages SQLite database operations"""
    
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                dex TEXT,
                token TEXT,
                base_currency TEXT,
                price REAL,
                volume REAL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                token TEXT,
                buy_dex TEXT,
                buy_price REAL,
                sell_dex TEXT,
                sell_price REAL,
                profit_percent REAL
            )
        ''')
        
        self.conn.commit()
    
    def insert_price(self, timestamp: datetime, dex: str, token: str, 
                    base_currency: str, price: float, volume: float) -> None:
        """
        Insert a price record into the database
        
        Args:
            timestamp: When the price was recorded
            dex: Name of the DEX
            token: Token symbol
            base_currency: Base currency symbol
            price: Token price
            volume: Trading volume
        """
        self.cursor.execute('''
            INSERT INTO prices (timestamp, dex, token, base_currency, price, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, dex, token, base_currency, price, volume))
        self.conn.commit()
    
    def insert_arbitrage_opportunity(self, timestamp: datetime, token: str,
                                    buy_dex: str, buy_price: float,
                                    sell_dex: str, sell_price: float,
                                    profit_percent: float) -> None:
        """
        Insert an arbitrage opportunity into the database
        
        Args:
            timestamp: When the opportunity was found
            token: Token symbol
            buy_dex: DEX to buy from
            buy_price: Buy price
            sell_dex: DEX to sell to
            sell_price: Sell price
            profit_percent: Profit percentage
        """
        self.cursor.execute('''
            INSERT INTO arbitrage_opportunities 
            (timestamp, token, buy_dex, buy_price, sell_dex, sell_price, profit_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, token, buy_dex, buy_price, sell_dex, sell_price, profit_percent))
        self.conn.commit()
    
    def get_latest_prices(self) -> List[Tuple]:
        """
        Get the most recent prices for all DEX-token pairs
        
        Returns:
            List of tuples containing (dex, token, price, volume, timestamp)
        """
        self.cursor.execute('''
            SELECT dex, token, price, volume, timestamp
            FROM prices
            WHERE timestamp = (SELECT MAX(timestamp) FROM prices)
            ORDER BY dex, token
        ''')
        return self.cursor.fetchall()
    
    def get_price_for_token(self, token: str, dex: str, 
                           timestamp: datetime) -> Optional[float]:
        """
        Get price for a specific token on a specific DEX at a given timestamp
        
        Args:
            token: Token symbol
            dex: DEX name
            timestamp: Timestamp to query
            
        Returns:
            Price if found, None otherwise
        """
        self.cursor.execute('''
            SELECT price FROM prices
            WHERE dex = ? AND token = ? AND timestamp = ?
            ORDER BY id DESC LIMIT 1
        ''', (dex, token, timestamp))
        
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_latest_arbitrage_opportunities(self) -> List[Tuple]:
        """
        Get the most recent arbitrage opportunities
        
        Returns:
            List of tuples containing arbitrage opportunity details
        """
        self.cursor.execute('''
            SELECT token, buy_dex, buy_price, sell_dex, sell_price, profit_percent, timestamp
            FROM arbitrage_opportunities
            WHERE timestamp = (SELECT MAX(timestamp) FROM arbitrage_opportunities)
            ORDER BY profit_percent DESC
        ''')
        return self.cursor.fetchall()
    
    def clear_all_data(self) -> None:
        """Clear all data from the database"""
        self.cursor.execute("DELETE FROM prices")
        self.cursor.execute("DELETE FROM arbitrage_opportunities")
        self.conn.commit()
    
    def close(self) -> None:
        """Close the database connection"""
        self.conn.close()