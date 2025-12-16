"""
Main window for DEX Analyzer (PySide6 version).
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QToolBar, QStatusBar, QCheckBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence

from database.database_manager import DatabaseManager
from services.token_manager import TokenManager
from services.data_service import DataService
from gui.theme_manager import ThemeManager
from gui.widgets.available_tokens_table import AvailableTokensTable
from gui.widgets.tracked_tokens_table import TrackedTokensTable
from gui.widgets.current_prices_table import CurrentPricesTable
from gui.widgets.arbitrage_table import ArbitrageTable


class MainWindow(QMainWindow):
    """
    Main application window with tabs for different views.
    """

    def __init__(self):
        super().__init__()

        # Initialize backend services
        self.db_manager = DatabaseManager()
        self.token_manager = TokenManager(self.db_manager)
        self.data_service = DataService()

        # Initialize theme manager
        self.theme_manager = ThemeManager(self.app_instance, self.db_manager)

        # Setup UI
        self.setup_ui()

        # Apply initial theme
        self.theme_manager.apply_theme(self.theme_manager.current_theme)

        # Restore window state
        self.restore_window_state()

    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Window properties
        self.setWindowTitle("DEX Arbitrage Monitor")
        self.resize(1600, 1000)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        main_layout.addWidget(self.tab_widget)

        # Create tabs (placeholders for now)
        self.create_tabs()

        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.create_status_bar()

    def create_top_bar(self) -> QWidget:
        """
        Create top bar with title, status, and theme toggle.

        Returns:
            Top bar widget
        """
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(60)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 10, 20, 10)

        # Title
        title_label = QLabel("DEX Arbitrage Monitor")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title_label)

        # Spacer
        layout.addStretch()

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 11pt; color: #00aa66;")
        layout.addWidget(self.status_label)

        # Theme toggle button
        self.theme_toggle_btn = QPushButton("🌙 Dark")
        self.theme_toggle_btn.setFixedWidth(120)
        self.theme_toggle_btn.setToolTip("Toggle between dark and light theme (Ctrl+T)")
        self.theme_toggle_btn.clicked.connect(self.on_theme_toggle)
        layout.addWidget(self.theme_toggle_btn)

        return top_bar

    def create_toolbar(self):
        """
        Create toolbar with action buttons.
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Refresh action with Ctrl+R shortcut
        refresh_action = QAction("Refresh Prices", self)
        refresh_action.setStatusTip("Refresh current prices (Ctrl+R)")
        refresh_action.setShortcut(QKeySequence("Ctrl+R"))
        refresh_action.triggered.connect(self.on_refresh)
        toolbar.addAction(refresh_action)

        # Scan action with Ctrl+S shortcut
        scan_action = QAction("Scan Arbitrage", self)
        scan_action.setStatusTip("Scan for arbitrage opportunities (Ctrl+S)")
        scan_action.setShortcut(QKeySequence("Ctrl+S"))
        scan_action.triggered.connect(self.on_scan)
        toolbar.addAction(scan_action)


    def create_status_bar(self):
        """
        Create status bar at bottom of window.
        """
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    def create_tabs(self):
        """
        Create all tab widgets.
        """
        # Tab 1: Available Tokens
        self.available_tokens_table = AvailableTokensTable(
            self.token_manager,
            self.theme_manager,
            self
        )
        self.available_tokens_table.tokens_added.connect(self.on_tokens_added)
        self.tab_widget.addTab(self.available_tokens_table, "Available Tokens")

        # Tab 2: Tracked Tokens
        self.tracked_tokens_table = TrackedTokensTable(
            self.token_manager,
            self.theme_manager,
            self
        )
        self.tracked_tokens_table.threshold_updated.connect(self.on_threshold_updated)
        self.tracked_tokens_table.token_removed.connect(self.on_token_removed)
        self.tab_widget.addTab(self.tracked_tokens_table, "Tracked Tokens")

        # Tab 3: Current Prices
        self.current_prices_table = CurrentPricesTable(
            self.token_manager,
            self.data_service,
            self.theme_manager,
            self
        )
        self.tab_widget.addTab(self.current_prices_table, "Current Prices")

        # Tab 4: Arbitrage Opportunities
        self.arbitrage_table = ArbitrageTable(
            self.token_manager,
            self.data_service,
            self.theme_manager,
            self
        )
        self.tab_widget.addTab(self.arbitrage_table, "Arbitrage Opportunities")

    @Slot()
    def on_theme_toggle(self):
        """
        Handle theme toggle button click.
        """
        new_theme = self.theme_manager.toggle_theme()

        # Update button text and icon
        if new_theme == "dark":
            self.theme_toggle_btn.setText("🌙 Dark")
        else:
            self.theme_toggle_btn.setText("☀️ Light")

        # Update status
        self.status_label.setText(f"Theme changed to {new_theme.capitalize()}")

    @Slot()
    def on_refresh(self):
        """
        Handle refresh action - refreshes prices on all 3 tabs with 1 API call.
        Updates: Available Tokens, Tracked Tokens, and Current Prices tabs.
        """
        self.set_status("Refreshing prices...")

        # Get all tokens (both available and tracked)
        available_tokens = self.token_manager.get_available_tokens()
        tracked_tokens_data = self.token_manager.get_tracked_tokens()
        tracked_tokens = [t for t, _ in tracked_tokens_data]

        # Combine all tokens
        all_tokens = available_tokens + tracked_tokens

        if not all_tokens:
            self.set_status("No tokens to refresh")
            return

        # Extract symbols
        token_symbols = [t.symbol for t in all_tokens]
        dex_keys = ["uniswap_v3", "pancakeswap_v3", "sushiswap", "curve"]

        # Bulk fetch all prices (1 API CALL!)
        try:
            all_prices = self.data_service.get_bulk_prices_all_dexes(token_symbols, dex_keys)

            # Update Available Tokens table
            if hasattr(self, 'available_tokens_table'):
                self.update_available_tokens_prices(all_prices)

            # Update Tracked Tokens table
            if hasattr(self, 'tracked_tokens_table'):
                self.update_tracked_tokens_prices(all_prices)

            # Update Current Prices table
            if hasattr(self, 'current_prices_table'):
                self.update_current_prices_table(all_prices)

            self.set_status(f"Refreshed prices for {len(all_tokens)} tokens")

        except Exception as e:
            self.set_status(f"Error refreshing prices: {str(e)}")

    def update_available_tokens_prices(self, all_prices):
        """
        Update prices in Available Tokens table.

        Args:
            all_prices: Dict of {symbol: {dex_key: price_data}}
        """
        from utils import format_price

        table = self.available_tokens_table.table

        for row in range(table.rowCount()):
            symbol_item = table.item(row, 1)  # Symbol column
            if not symbol_item:
                continue

            symbol = symbol_item.text()
            if symbol not in all_prices:
                continue

            # Get average price across all DEXes
            dex_prices = all_prices[symbol]
            prices = [data.get('price_usd', 0) for data in dex_prices.values() if data.get('price_usd', 0) > 0]
            volumes = [data.get('volume_24h', 0) for data in dex_prices.values() if data.get('volume_24h', 0) > 0]
            liquidities = [data.get('liquidity_usd', 0) for data in dex_prices.values() if data.get('liquidity_usd', 0) > 0]

            avg_price = sum(prices) / len(prices) if prices else 0
            total_volume = sum(volumes) if volumes else 0
            avg_liquidity = sum(liquidities) / len(liquidities) if liquidities else 0

            # Update Price column (index 3)
            price_text = format_price(avg_price) if avg_price > 0 else "$0.00"
            price_item = table.item(row, 3)
            if price_item:
                price_item.setText(price_text)

            # Update Volume column (index 4)
            volume_text = f"${total_volume:,.0f}" if total_volume > 0 else "$0"
            volume_item = table.item(row, 4)
            if volume_item:
                volume_item.setText(volume_text)

            # Update Liquidity column (index 5)
            liquidity_text = f"${avg_liquidity:,.0f}" if avg_liquidity > 0 else "$0"
            liquidity_item = table.item(row, 5)
            if liquidity_item:
                liquidity_item.setText(liquidity_text)

    def update_tracked_tokens_prices(self, all_prices):
        """
        Update prices in Tracked Tokens table.

        Args:
            all_prices: Dict of {symbol: {dex_key: price_data}}
        """
        from utils import format_price

        table = self.tracked_tokens_table.table

        for row in range(table.rowCount()):
            symbol_item = table.item(row, 0)  # Symbol column
            if not symbol_item:
                continue

            symbol = symbol_item.text()
            if symbol not in all_prices:
                continue

            # Get data from all DEXes
            dex_prices = all_prices[symbol]
            prices = [data.get('price_usd', 0) for data in dex_prices.values() if data.get('price_usd', 0) > 0]
            price_changes = [data.get('price_change_24h', 0) for data in dex_prices.values()]
            liquidities = [data.get('liquidity_usd', 0) for data in dex_prices.values() if data.get('liquidity_usd', 0) > 0]

            avg_price = sum(prices) / len(prices) if prices else 0
            avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
            avg_liquidity = sum(liquidities) / len(liquidities) if liquidities else 0

            # Update Price column (index 2)
            price_text = format_price(avg_price) if avg_price > 0 else "$0.00"
            price_item = table.item(row, 2)
            if price_item:
                price_item.setText(price_text)

            # Update Volatility column (index 3) based on 24h change
            volatility = "High" if abs(avg_change) > 5 else "Medium" if abs(avg_change) > 2 else "Low"
            volatility_item = table.item(row, 3)
            if volatility_item:
                volatility_item.setText(volatility)

            # Update Liquidity column (index 4)
            liquidity_text = f"${avg_liquidity:,.0f}" if avg_liquidity > 0 else "$0"
            liquidity_item = table.item(row, 4)
            if liquidity_item:
                liquidity_item.setText(liquidity_text)

    def update_current_prices_table(self, all_prices):
        """
        Update the Current Prices table with bulk fetched data.

        Args:
            all_prices: Dict of {symbol: {dex_key: price_data}}
        """
        # Clear and populate the prices cache
        self.current_prices_table.prices_cache.clear()

        for symbol, dex_prices in all_prices.items():
            self.current_prices_table.prices_cache[symbol] = {}
            for dex_key, price_data in dex_prices.items():
                if price_data:
                    self.current_prices_table.prices_cache[symbol][dex_key] = price_data.get('price_usd', 0.0)

        # Update the table display
        self.current_prices_table.update_table()

    @Slot()
    def on_scan(self):
        """
        Handle scan action - scans for arbitrage opportunities.
        """
        self.set_status("Scanning for arbitrage opportunities...")

        # Switch to arbitrage tab and trigger scan
        if hasattr(self, 'arbitrage_table'):
            self.tab_widget.setCurrentIndex(3)  # Arbitrage tab
            self.arbitrage_table.scan_now()

    @Slot(list)
    def on_tokens_added(self, token_ids):
        """
        Handle tokens being added to tracking.

        Args:
            token_ids: List of token IDs that were added
        """
        self.set_status(f"Added {len(token_ids)} token(s) to tracking")

        # Refresh available tokens table to remove added tokens
        if hasattr(self, 'available_tokens_table'):
            self.available_tokens_table.refresh()

        # Refresh tracked tokens table if it exists
        if hasattr(self, 'tracked_tokens_table'):
            self.tracked_tokens_table.refresh()

    @Slot(int, float, str)
    def on_threshold_updated(self, token_id, value, mode):
        """
        Handle threshold being updated.

        Args:
            token_id: Token ID that was updated
            value: New threshold value
            mode: New threshold mode
        """
        mode_text = "%" if mode == "percentage" else "$"
        self.set_status(f"Threshold updated to {value:.2f}{mode_text}")

    @Slot(int)
    def on_token_removed(self, token_id):
        """
        Handle token being removed from tracking.

        Args:
            token_id: Token ID that was removed
        """
        self.set_status("Token removed from tracking")

        # Refresh available tokens table to show removed token
        if hasattr(self, 'available_tokens_table'):
            self.available_tokens_table.refresh()

    def set_status(self, message: str):
        """
        Set status message in both top bar and status bar.

        Args:
            message: Status message to display
        """
        self.status_label.setText(message)
        self.statusBar().showMessage(message)

    def restore_window_state(self):
        """
        Restore window size, position, and tab selection from database.
        """
        try:
            # Restore window geometry
            width = self.db_manager.get_preference("window_width")
            height = self.db_manager.get_preference("window_height")
            x = self.db_manager.get_preference("window_x")
            y = self.db_manager.get_preference("window_y")

            if width and height:
                self.resize(int(width), int(height))

            if x is not None and y is not None:
                self.move(int(x), int(y))

            # Restore last active tab
            last_tab = self.db_manager.get_preference("last_tab_index")
            if last_tab is not None:
                tab_index = int(last_tab)
                if 0 <= tab_index < self.tab_widget.count():
                    self.tab_widget.setCurrentIndex(tab_index)

        except Exception as e:
            # If restoration fails, just use defaults
            print(f"Could not restore window state: {e}")

    def save_window_state(self):
        """
        Save window size, position, and tab selection to database.
        """
        try:
            # Save window geometry
            self.db_manager.set_preference("window_width", str(self.width()))
            self.db_manager.set_preference("window_height", str(self.height()))
            self.db_manager.set_preference("window_x", str(self.x()))
            self.db_manager.set_preference("window_y", str(self.y()))

            # Save current tab
            current_tab = self.tab_widget.currentIndex()
            self.db_manager.set_preference("last_tab_index", str(current_tab))

        except Exception as e:
            print(f"Could not save window state: {e}")

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Save window state before closing
        self.save_window_state()

        # Clean up database connection
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

        event.accept()

    @property
    def app_instance(self):
        """
        Get QApplication instance.

        Returns:
            QApplication instance
        """
        from PySide6.QtWidgets import QApplication
        return QApplication.instance()
