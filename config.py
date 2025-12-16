class Config:
    """
    Application configuration constants.

    This application uses CoinGecko API for real cryptocurrency prices
    and simulates DEX-specific price variations for arbitrage detection.
    """

    # DEX Configuration - 4 most popular DEXes (display names only)
    DEX_CONFIG = {
        "uniswap_v3": {
            "name": "Uniswap V3",
        },
        "pancakeswap_v3": {
            "name": "PancakeSwap V3",
        },
        "sushiswap": {
            "name": "SushiSwap",
        },
        "curve": {
            "name": "Curve Finance",
        }
    }

    # 40 Most Popular Tokens Configuration
    TOKENS_CONFIG = [
        {"symbol": "WBTC", "name": "Wrapped Bitcoin", "decimals": 8},
        {"symbol": "ETH", "name": "Ethereum", "decimals": 18},
        {"symbol": "USDT", "name": "Tether", "decimals": 6},
        {"symbol": "USDC", "name": "USD Coin", "decimals": 6},
        {"symbol": "BNB", "name": "Binance Coin", "decimals": 18},
        {"symbol": "XRP", "name": "Ripple", "decimals": 6},
        {"symbol": "ADA", "name": "Cardano", "decimals": 6},
        {"symbol": "SOL", "name": "Solana", "decimals": 9},
        {"symbol": "DOGE", "name": "Dogecoin", "decimals": 8},
        {"symbol": "MATIC", "name": "Polygon", "decimals": 18},
        {"symbol": "DOT", "name": "Polkadot", "decimals": 10},
        {"symbol": "AVAX", "name": "Avalanche", "decimals": 18},
        {"symbol": "LINK", "name": "Chainlink", "decimals": 18},
        {"symbol": "UNI", "name": "Uniswap", "decimals": 18},
        {"symbol": "ATOM", "name": "Cosmos", "decimals": 6},
        {"symbol": "LTC", "name": "Litecoin", "decimals": 8},
        {"symbol": "ETC", "name": "Ethereum Classic", "decimals": 18},
        {"symbol": "XLM", "name": "Stellar", "decimals": 7},
        {"symbol": "BCH", "name": "Bitcoin Cash", "decimals": 8},
        {"symbol": "ALGO", "name": "Algorand", "decimals": 6},
        {"symbol": "SHIB", "name": "Shiba Inu", "decimals": 18},
        {"symbol": "TRX", "name": "Tron", "decimals": 6},
        {"symbol": "LEO", "name": "UNUS SED LEO", "decimals": 18},
        {"symbol": "FTT", "name": "FTX Token", "decimals": 18},
        {"symbol": "CRO", "name": "Crypto.com Coin", "decimals": 8},
        {"symbol": "NEAR", "name": "NEAR Protocol", "decimals": 24},
        {"symbol": "APE", "name": "ApeCoin", "decimals": 18},
        {"symbol": "MANA", "name": "Decentraland", "decimals": 18},
        {"symbol": "SAND", "name": "The Sandbox", "decimals": 18},
        {"symbol": "AXS", "name": "Axie Infinity", "decimals": 18},
        {"symbol": "EOS", "name": "EOS", "decimals": 4},
        {"symbol": "AAVE", "name": "Aave", "decimals": 18},
        {"symbol": "MKR", "name": "Maker", "decimals": 18},
        {"symbol": "SNX", "name": "Synthetix", "decimals": 18},
        {"symbol": "GRT", "name": "The Graph", "decimals": 18},
        {"symbol": "FTM", "name": "Fantom", "decimals": 18},
        {"symbol": "RUNE", "name": "THORChain", "decimals": 18},
        {"symbol": "LRC", "name": "Loopring", "decimals": 18},
        {"symbol": "1INCH", "name": "1inch", "decimals": 18},
        {"symbol": "ENJ", "name": "Enjin Coin", "decimals": 18}
    ]

    # Arbitrage Configuration
    DEFAULT_THRESHOLD = 1.0  # percentage
    DEFAULT_THRESHOLD_MODE = "percentage"  # or "dollar"
    AUTO_REFRESH_INTERVAL = 30  # seconds

    # Database Configuration
    DATABASE_NAME = "dex_analyzer.db"

    # GUI Configuration
    WINDOW_TITLE = "DEX Arbitrage Monitor"
    WINDOW_SIZE = "1600x1000"
    DEFAULT_THEME = "dark"  # "dark" or "light"

    # Color Configuration
    HIGH_PROFIT_COLOR = "#90EE90"  # Light green
    MEDIUM_PROFIT_COLOR = "#FFFFE0"  # Light yellow
    HIGH_PROFIT_THRESHOLD = 5.0  # percentage
    MEDIUM_PROFIT_THRESHOLD = 3.0  # percentage

    # Cache Configuration
    PRICE_CACHE_TTL = 30  # seconds - CoinGecko API cache duration
