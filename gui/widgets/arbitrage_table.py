"""
Arbitrage Opportunities Table widget for DEX Analyzer.
Displays profitable arbitrage opportunities with statistics.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QCheckBox, QFrame, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QColor, QAction

from gui.threads.arbitrage_scanner import ArbitrageScannerThread
from utils import format_price


class ArbitrageTable(QWidget):
    """
    Table widget showing arbitrage opportunities with statistics.
    """

    def __init__(self, token_manager, data_service, theme_manager, parent=None):
        super().__init__(parent)

        self.token_manager = token_manager
        self.data_service = data_service
        self.theme_manager = theme_manager
        self.scanner_thread = None
        self.opportunities = []

        # Auto-scan timer
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.scan_opportunities)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title and controls
        controls = QHBoxLayout()

        title = QLabel("💰 Arbitrage Opportunities")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        controls.addWidget(title)

        controls.addStretch()

        self.scan_btn = QPushButton("Scan for Opportunities")
        self.scan_btn.setObjectName("primaryButton")
        self.scan_btn.setFixedWidth(180)
        self.scan_btn.setToolTip("Scan all DEXes for arbitrage opportunities (Ctrl+S)")
        self.scan_btn.clicked.connect(self.on_scan_clicked)
        controls.addWidget(self.scan_btn)

        self.auto_scan_cb = QCheckBox("Auto-scan (60s)")
        self.auto_scan_cb.setToolTip("Automatically scan for opportunities every 60 seconds")
        self.auto_scan_cb.stateChanged.connect(self.toggle_auto_scan)
        controls.addWidget(self.auto_scan_cb)

        self.status_label = QLabel("Ready")
        controls.addWidget(self.status_label)

        layout.addLayout(controls)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Token", "Buy From", "Buy Price", "Sell To", "Sell Price",
            "Profit $", "Profit %", "Threshold", "Status"
        ])

        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        # Column widths
        header = self.table.horizontalHeader()
        widths = [80, 120, 100, 120, 100, 100, 100, 100, 120]
        for i, width in enumerate(widths):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(i, width)

        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

    @Slot()
    def on_scan_clicked(self):
        self.scan_opportunities()

    def scan_opportunities(self):
        if self.scanner_thread and self.scanner_thread.isRunning():
            return

        tracked = self.token_manager.get_tracked_tokens()
        if not tracked:
            self.status_label.setText("No tracked tokens")
            return

        self.scan_btn.setEnabled(False)
        self.status_label.setText("Scanning...")
        self.opportunities.clear()
        self.table.setRowCount(0)

        self.scanner_thread = ArbitrageScannerThread(tracked, self.data_service)
        self.scanner_thread.opportunity_found.connect(self.on_opportunity_found)
        self.scanner_thread.finished.connect(self.on_scan_complete)
        self.scanner_thread.error.connect(self.on_scan_error)
        self.scanner_thread.start()

    @Slot(dict)
    def on_opportunity_found(self, opp):
        self.opportunities.append(opp)
        self.add_opportunity_row(opp)

    @Slot(int)
    def on_scan_complete(self, total):
        self.scan_btn.setEnabled(True)
        self.status_label.setText(f"Found {total} opportunities")

        # Show info if no opportunities found
        if total == 0:
            QMessageBox.information(
                self,
                "No Opportunities",
                "No arbitrage opportunities found that meet the threshold criteria.\n\nTry lowering your thresholds or waiting for market conditions to change."
            )

    @Slot(str)
    def on_scan_error(self, error_msg):
        """Handle error from scanner thread."""
        self.scan_btn.setEnabled(True)
        self.status_label.setText("Error scanning")

        QMessageBox.critical(
            self,
            "Scan Error",
            f"An error occurred while scanning for opportunities:\n{error_msg}\n\nPlease check your internet connection and try again."
        )

    def add_opportunity_row(self, opp):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Token
        self.table.setItem(row, 0, self.create_center_item(opp['symbol']))

        # Buy From & Price
        self.table.setItem(row, 1, QTableWidgetItem(self.format_dex(opp['buy_dex'])))
        self.table.setItem(row, 2, self.create_right_item(format_price(opp['buy_price'])))

        # Sell To & Price
        self.table.setItem(row, 3, QTableWidgetItem(self.format_dex(opp['sell_dex'])))
        self.table.setItem(row, 4, self.create_right_item(format_price(opp['sell_price'])))

        # Profit $
        profit_usd_item = self.create_right_item(format_price(opp['profit_usd']))
        self.table.setItem(row, 5, profit_usd_item)

        # Profit %
        profit_pct_item = self.create_right_item(f"{opp['profit_pct']:.2f}%")
        self.table.setItem(row, 6, profit_pct_item)

        # Threshold
        threshold_mode = "%" if opp['threshold_mode'] == "percentage" else "$"
        self.table.setItem(row, 7, self.create_center_item(
            f"{opp['threshold_value']:.2f}{threshold_mode}"
        ))

        # Status
        if opp['threshold_met']:
            if opp['profit_pct'] >= 5.0:
                status = "🟢 EXCELLENT"
                color = QColor("#00ff88")
            elif opp['profit_pct'] >= 2.0:
                status = "🟡 GOOD"
                color = QColor("#ffd700")
            else:
                status = "✅ OK"
                color = QColor("#00cc66")
        else:
            status = "❌ Below Threshold"
            color = QColor("#808080")

        status_item = self.create_center_item(status)
        status_item.setForeground(color)
        self.table.setItem(row, 8, status_item)

        # Apply row color
        self.apply_row_color(row, opp['profit_pct'], opp['threshold_met'])

    def apply_row_color(self, row, profit_pct, threshold_met):
        if not threshold_met:
            return

        if profit_pct >= 5.0:
            bg_color = QColor("#003322" if self.theme_manager.is_dark_theme() else "#e6ffe6")
        elif profit_pct >= 2.0:
            bg_color = QColor("#332200" if self.theme_manager.is_dark_theme() else "#fffae6")
        else:
            return

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(bg_color)

    def format_dex(self, dex_key):
        names = {
            "uniswap_v3": "Uniswap V3",
            "pancakeswap_v3": "PancakeSwap V3",
            "sushiswap": "SushiSwap",
            "curve": "Curve"
        }
        return names.get(dex_key, dex_key)

    def create_center_item(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def create_right_item(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item

    @Slot(int)
    def toggle_auto_scan(self, state):
        if state == Qt.CheckState.Checked.value:
            self.scan_timer.start(60000)  # 60 seconds
            self.scan_opportunities()
        else:
            self.scan_timer.stop()

    @Slot()
    def show_context_menu(self, position):
        """
        Show context menu on right-click.

        Args:
            position: Position where right-click occurred
        """
        # Get selected row
        item = self.table.itemAt(position)
        if not item:
            return

        row = item.row()

        # Get opportunity data from row
        token = self.table.item(row, 0).text()
        buy_dex = self.table.item(row, 1).text()
        buy_price = self.table.item(row, 2).text()
        sell_dex = self.table.item(row, 3).text()
        sell_price = self.table.item(row, 4).text()
        profit_usd = self.table.item(row, 5).text()
        profit_pct = self.table.item(row, 6).text()

        # Create context menu
        menu = QMenu(self)

        # Copy actions
        copy_token_action = QAction("Copy Token Symbol", self)
        copy_token_action.triggered.connect(lambda: self.copy_to_clipboard(token))
        menu.addAction(copy_token_action)

        copy_buy_action = QAction(f"Copy Buy Info ({buy_dex})", self)
        copy_buy_action.triggered.connect(lambda: self.copy_to_clipboard(f"{buy_dex}: {buy_price}"))
        menu.addAction(copy_buy_action)

        copy_sell_action = QAction(f"Copy Sell Info ({sell_dex})", self)
        copy_sell_action.triggered.connect(lambda: self.copy_to_clipboard(f"{sell_dex}: {sell_price}"))
        menu.addAction(copy_sell_action)

        menu.addSeparator()

        copy_profit_action = QAction("Copy Profit Info", self)
        copy_profit_action.triggered.connect(lambda: self.copy_to_clipboard(f"{profit_usd} ({profit_pct})"))
        menu.addAction(copy_profit_action)

        menu.addSeparator()

        # Copy full opportunity as text
        copy_all_action = QAction("Copy Full Opportunity", self)
        full_text = f"{token}: Buy from {buy_dex} at {buy_price}, Sell to {sell_dex} at {sell_price} | Profit: {profit_usd} ({profit_pct})"
        copy_all_action.triggered.connect(lambda: self.copy_to_clipboard(full_text))
        menu.addAction(copy_all_action)

        # Show menu
        menu.exec(self.table.viewport().mapToGlobal(position))

    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def scan_now(self):
        """Public method to trigger scan from outside."""
        self.scan_opportunities()

    def refresh_opportunities(self):
        """Public method to refresh from outside."""
        if self.auto_scan_cb.isChecked():
            self.scan_opportunities()

    def refresh(self):
        if self.auto_scan_cb.isChecked():
            self.scan_opportunities()
