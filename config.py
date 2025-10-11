class Config:
    """Application configuration constants"""
    
    # API Configuration
    BITQUERY_URL = "https://streaming.bitquery.io/graphql"
    API_TIMEOUT = 1  # seconds
    REQUEST_DELAY = 0.5  # seconds between API requests
    
    # DEX Configuration
    SUPPORTED_DEXES = ["Uniswap", "PancakeSwap", "SushiSwap"]
    SUPPORTED_TOKENS = ["WETH", "WBTC", "USDC", "DAI"]
    BASE_CURRENCY = "USDT"
    
    # Arbitrage Configuration
    DEFAULT_THRESHOLD = 0.01  # percentage
    AUTO_REFRESH_INTERVAL = 1  # seconds
    
    # Network Configuration
    NETWORK_MAPPING = {
        "Uniswap": "eth",
        "PancakeSwap": "bsc",
        "SushiSwap": "eth"
    }
    
    # Token Addresses
    TOKEN_ADDRESSES = {
        "ethereum": {
            "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "WBTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
            "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "DAI": "0x6b175474e89094c44da98b954eedeac495271d0f",
            "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7"
        },
        "bsc": {
            "WETH": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            "WBTC": "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c",
            "USDC": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
            "DAI": "0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3",
            "USDT": "0x55d398326f99059ff775485246999027b3197955"
        }
    }
    
    # Database Configuration
    DATABASE_NAME = "dex_prices.db"
    
    # GUI Configuration
    WINDOW_TITLE = "DEX Arbitrage Monitor"
    WINDOW_SIZE = "1200x800"
    
    # Color Configuration
    HIGH_PROFIT_COLOR = "#90EE90"  # Light green
    MEDIUM_PROFIT_COLOR = "#FFFFE0"  # Light yellow
    HIGH_PROFIT_THRESHOLD = 0.05  # percentage
    MEDIUM_PROFIT_THRESHOLD = 0.03  # percentage