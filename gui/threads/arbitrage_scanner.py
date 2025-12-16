"""
Arbitrage Scanner Thread for DEX Analyzer.
Background thread for detecting arbitrage opportunities.
"""

from PySide6.QtCore import QThread, Signal


class ArbitrageScannerThread(QThread):
    """
    Background thread for scanning arbitrage opportunities.
    """

    # Signals
    opportunity_found = Signal(dict)  # opportunity data
    progress = Signal(int, int)  # current, total
    finished = Signal(int)  # total opportunities found
    error = Signal(str)

    def __init__(self, tracked_tokens, data_service):
        """
        Initialize scanner thread.

        Args:
            tracked_tokens: List of (Token, TrackedToken) tuples
            data_service: DataService instance
        """
        super().__init__()
        self.tracked_tokens = tracked_tokens
        self.data_service = data_service
        self.dex_keys = ["uniswap_v3", "pancakeswap_v3", "sushiswap", "curve"]

    def run(self):
        """
        Scan for arbitrage opportunities.
        OPTIMIZED: Fetches all tokens with a single API call.
        """
        try:
            if self.isInterruptionRequested():
                return

            opportunities_found = 0
            total = len(self.tracked_tokens)

            # Step 1: Extract token symbols
            token_symbols = [token.symbol for token, _ in self.tracked_tokens]

            # Step 2: Bulk fetch all prices (1 API CALL!)
            self.progress.emit(0, total)

            all_prices = self.data_service.get_bulk_prices_all_dexes(
                token_symbols,
                self.dex_keys
            )

            # Step 3: Analyze each token for arbitrage opportunities
            for i, (token, tracked) in enumerate(self.tracked_tokens):
                if self.isInterruptionRequested():
                    return

                # Get prices for this token
                symbol = token.symbol
                if symbol in all_prices:
                    # Extract price_usd from each DEX
                    prices = {}
                    for dex_key in self.dex_keys:
                        if dex_key in all_prices[symbol]:
                            price_data = all_prices[symbol][dex_key]
                            if price_data and price_data.get('price_usd'):
                                prices[dex_key] = price_data['price_usd']

                    # Find best buy/sell opportunities
                    if len(prices) >= 2:
                        opps = self.find_opportunities(token, tracked, prices)
                        opportunities_found += len(opps)
                        for opp in opps:
                            self.opportunity_found.emit(opp)

                self.progress.emit(i + 1, total)

            self.finished.emit(opportunities_found)

        except Exception as e:
            self.error.emit(str(e))

    def find_opportunities(self, token, tracked, prices):
        """
        Find arbitrage opportunities for a token.

        Args:
            token: Token object
            tracked: TrackedToken object
            prices: Dict of {dex_key: price}

        Returns:
            List of opportunity dicts
        """
        opportunities = []
        dex_list = list(prices.items())

        for i, (buy_dex, buy_price) in enumerate(dex_list):
            for sell_dex, sell_price in dex_list[i+1:]:
                if buy_price >= sell_price:
                    continue

                # Calculate profit
                profit_usd = sell_price - buy_price
                profit_pct = (profit_usd / buy_price * 100) if buy_price > 0 else 0

                # Check threshold
                threshold_met = False
                if tracked.threshold_mode == "percentage":
                    threshold_met = profit_pct >= tracked.threshold_value
                else:  # dollar
                    threshold_met = profit_usd >= tracked.threshold_value

                opportunity = {
                    'token_id': token.id,
                    'symbol': token.symbol,
                    'name': token.name,
                    'buy_dex': buy_dex,
                    'buy_price': buy_price,
                    'sell_dex': sell_dex,
                    'sell_price': sell_price,
                    'profit_usd': profit_usd,
                    'profit_pct': profit_pct,
                    'threshold_value': tracked.threshold_value,
                    'threshold_mode': tracked.threshold_mode,
                    'threshold_met': threshold_met
                }
                opportunities.append(opportunity)

        # Sort by profit percentage descending
        opportunities.sort(key=lambda x: x['profit_pct'], reverse=True)
        return opportunities
