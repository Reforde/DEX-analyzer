"""
Current Prices Table widget for DEX Analyzer.
Displays real-time prices from multiple DEXes.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QColor

from gui.threads.price_fetcher import PriceFetcherThread
from utils import format_price


class CurrentPricesTable(QWidget):
    """
    Table widget showing current prices from multiple DEXes.
    """

    def __init__(self, token_manager, data_service, theme_manager, parent=None):
        super().__init__(parent)

        self.token_manager = token_manager
        self.data_service = data_service
        self.theme_manager = theme_manager
        self.fetcher_thread = None
        self.prices_cache = {}  # {symbol: {dex: price}}

        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_prices)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Controls
        controls = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh Prices")
        self.refresh_btn.setFixedWidth(150)
        self.refresh_btn.setToolTip("Fetch latest prices from all DEXes (Ctrl+R)")
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        controls.addWidget(self.refresh_btn)

        self.auto_refresh_cb = QCheckBox("Auto-refresh (30s)")
        self.auto_refresh_cb.setToolTip("Automatically refresh prices every 30 seconds")
        self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
        controls.addWidget(self.auto_refresh_cb)

        controls.addStretch()

        self.status_label = QLabel("Ready")
        controls.addWidget(self.status_label)

        layout.addLayout(controls)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Symbol", "Name", "Uniswap V3", "PancakeSwap V3",
            "SushiSwap", "Curve", "Best Price", "Worst Price", "Spread %"
        ])

        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        # Column widths
        header = self.table.horizontalHeader()
        for i in range(9):
            if i in [0, 2, 3, 4, 5]:  # Symbol and DEX columns
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                header.resizeSection(i, 100)
            elif i == 1:  # Name
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:  # Price columns
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                header.resizeSection(i, 110)

        layout.addWidget(self.table)

        # Info
        self.info_label = QLabel("Click Refresh to load prices from DEXes")
        self.info_label.setStyleSheet("color: #808080; font-style: italic;")
        layout.addWidget(self.info_label)

    @Slot()
    def on_refresh_clicked(self):
        tracked = self.token_manager.get_tracked_tokens()
        if not tracked:
            self.status_label.setText("No tracked tokens")
            return

        self.refresh_prices()

    def refresh_prices(self):
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            return

        tracked = self.token_manager.get_tracked_tokens()
        tokens = [t for t, _ in tracked]

        if not tokens:
            return

        self.refresh_btn.setEnabled(False)
        self.status_label.setText("Fetching prices...")
        self.prices_cache.clear()

        self.fetcher_thread = PriceFetcherThread(tokens, self.data_service)
        self.fetcher_thread.price_fetched.connect(self.on_price_received)
        self.fetcher_thread.finished.connect(self.on_fetch_complete)
        self.fetcher_thread.error.connect(self.on_fetch_error)
        self.fetcher_thread.start()

    @Slot(str, str, dict)
    def on_price_received(self, symbol, dex_key, price_data):
        if symbol not in self.prices_cache:
            self.prices_cache[symbol] = {}
        self.prices_cache[symbol][dex_key] = price_data.get('price_usd', 0.0)

    @Slot()
    def on_fetch_complete(self):
        self.update_table()
        self.refresh_btn.setEnabled(True)

        # Show results or warning if no prices fetched
        if len(self.prices_cache) == 0:
            self.status_label.setText("No prices fetched")
            QMessageBox.warning(
                self,
                "No Prices",
                "Could not fetch prices from any DEX. Please check your internet connection and try again."
            )
        else:
            self.status_label.setText(f"Updated {len(self.prices_cache)} tokens")

    @Slot(str)
    def on_fetch_error(self, error_msg):
        """Handle error from price fetcher thread."""
        self.refresh_btn.setEnabled(True)
        self.status_label.setText("Error fetching prices")

        QMessageBox.critical(
            self,
            "Price Fetch Error",
            f"An error occurred while fetching prices:\n{error_msg}\n\nPlease try again later."
        )

    def update_table(self):
        tracked = self.token_manager.get_tracked_tokens()
        self.table.setRowCount(0)

        for token, _ in tracked:
            if token.symbol in self.prices_cache:
                self.add_price_row(token, self.prices_cache[token.symbol])

    def add_price_row(self, token, prices):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Symbol & Name
        self.table.setItem(row, 0, self.create_center_item(token.symbol))
        self.table.setItem(row, 1, QTableWidgetItem(token.name))

        # DEX prices
        dex_keys = ["uniswap_v3", "pancakeswap_v3", "sushiswap", "curve"]
        price_values = []

        for i, dex_key in enumerate(dex_keys, start=2):
            price = prices.get(dex_key, 0.0)
            price_values.append(price)
            price_text = format_price(price) if price > 0 else "N/A"
            self.table.setItem(row, i, self.create_right_item(price_text))

        # Best/Worst/Spread
        valid_prices = [p for p in price_values if p > 0]
        if valid_prices:
            best = max(valid_prices)
            worst = min(valid_prices)
            spread = ((best - worst) / worst * 100) if worst > 0 else 0

            self.table.setItem(row, 6, self.create_right_item(format_price(best)))
            self.table.setItem(row, 7, self.create_right_item(format_price(worst)))

            spread_item = self.create_right_item(f"{spread:.2f}%")
            if spread >= 2.0:
                spread_item.setForeground(QColor("#00ff88"))
            elif spread >= 1.0:
                spread_item.setForeground(QColor("#ffd700"))
            self.table.setItem(row, 8, spread_item)

    def create_center_item(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def create_right_item(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item

    @Slot(int)
    def toggle_auto_refresh(self, state):
        if state == Qt.CheckState.Checked.value:
            self.refresh_timer.start(30000)  # 30 seconds
            self.refresh_prices()
        else:
            self.refresh_timer.stop()

    def refresh(self):
        if self.auto_refresh_cb.isChecked():
            self.refresh_prices()
