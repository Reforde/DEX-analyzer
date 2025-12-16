"""
Price Fetcher Thread for DEX Analyzer.
Background thread for fetching token prices from multiple DEXes.
"""

from PySide6.QtCore import QThread, Signal


class PriceFetcherThread(QThread):
    """
    Background thread for fetching prices without blocking UI.
    """

    # Signals
    price_fetched = Signal(str, str, dict)  # symbol, dex_key, price_data
    progress = Signal(int, int)  # current, total
    finished = Signal()
    error = Signal(str)

    def __init__(self, tokens, data_service, dex_keys=None):
        """
        Initialize price fetcher thread.

        Args:
            tokens: List of Token objects to fetch prices for
            data_service: DataService instance
            dex_keys: List of DEX keys to fetch from (default: all 4)
        """
        super().__init__()
        self.tokens = tokens
        self.data_service = data_service
        self.dex_keys = dex_keys or ["uniswap_v3", "pancakeswap_v3", "sushiswap", "curve"]

    def run(self):
        """
        Run the price fetching process.
        OPTIMIZED: Fetches all tokens with a single API call using bulk method.
        """
        try:
            if self.isInterruptionRequested():
                return

            # Extract token symbols
            token_symbols = [token.symbol for token in self.tokens]

            # Step 1: Bulk fetch all prices (1 API CALL for all tokens & DEXes!)
            self.progress.emit(0, 1)

            all_prices = self.data_service.get_bulk_prices_all_dexes(
                token_symbols,
                self.dex_keys
            )

            # Step 2: Emit results for each token-DEX combination
            total_operations = len(self.tokens) * len(self.dex_keys)
            current = 0

            for token in self.tokens:
                if self.isInterruptionRequested():
                    return

                symbol = token.symbol
                if symbol in all_prices:
                    for dex_key in self.dex_keys:
                        if dex_key in all_prices[symbol]:
                            price_data = all_prices[symbol][dex_key]
                            self.price_fetched.emit(symbol, dex_key, price_data)

                        current += 1
                        self.progress.emit(current, total_operations)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
