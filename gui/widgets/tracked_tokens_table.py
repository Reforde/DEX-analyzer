"""
Tracked Tokens Table widget for DEX Analyzer.
Displays tracked tokens with editable thresholds.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QMessageBox, QMenu, QDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QAction

from gui.widgets.threshold_dialog import ThresholdEditDialog


class TrackedTokensTable(QWidget):
    """
    Table widget showing tracked tokens with editable thresholds.
    """

    # Signals
    threshold_updated = Signal(int, float, str)  # token_id, value, mode
    token_removed = Signal(int)  # token_id

    def __init__(self, token_manager, theme_manager, parent=None):
        """
        Initialize tracked tokens table.

        Args:
            token_manager: TokenManager instance for data access
            theme_manager: ThemeManager instance for theming
            parent: Parent widget
        """
        super().__init__(parent)

        self.token_manager = token_manager
        self.theme_manager = theme_manager

        self.setup_ui()
        self.load_tokens()

    def setup_ui(self):
        """
        Set up the user interface.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Tracked Tokens")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Hint
        hint_label = QLabel("Double-click threshold to edit | Click Remove to stop tracking")
        hint_label.setStyleSheet("color: #808080; font-style: italic;")
        header_layout.addWidget(hint_label)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Symbol", "Token Name", "Price (USD)", "Volatility",
            "Liquidity", "Threshold", "Mode", "Actions"
        ])

        # Configure table
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 100)  # Symbol
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name stretches
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 120)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 100)  # Volatility
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 120)  # Liquidity
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 100)  # Threshold
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 80)  # Mode
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(7, 110)  # Actions - wider for Remove button

        # Connect signals
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # Footer section
        footer_layout = QHBoxLayout()

        # Info label
        self.info_label = QLabel("No tracked tokens")
        self.info_label.setStyleSheet("color: #808080;")
        footer_layout.addWidget(self.info_label)

        footer_layout.addStretch()

        layout.addLayout(footer_layout)

    def load_tokens(self):
        """
        Load tracked tokens from database.
        """
        # Get tracked tokens
        tracked = self.token_manager.get_tracked_tokens()

        # Clear table
        self.table.setRowCount(0)

        # Populate table
        for token, tracked_token in tracked:
            self.add_token_row(token, tracked_token)

        # Update info
        count = len(tracked)
        if count == 0:
            self.info_label.setText("No tracked tokens - Add tokens from 'Available Tokens' tab")
        elif count == 1:
            self.info_label.setText("Tracking 1 token")
        else:
            self.info_label.setText(f"Tracking {count} tokens")

    def add_token_row(self, token, tracked_token):
        """
        Add a tracked token row to the table.

        Args:
            token: Token object
            tracked_token: TrackedToken object
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Symbol
        symbol_item = QTableWidgetItem(token.symbol)
        symbol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 0, symbol_item)

        # Name
        name_item = QTableWidgetItem(token.name)
        name_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 1, name_item)

        # Price (placeholder)
        price_item = QTableWidgetItem("$0.00")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 2, price_item)

        # Volatility (placeholder)
        volatility_item = QTableWidgetItem("Low")
        volatility_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        volatility_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 3, volatility_item)

        # Liquidity (placeholder)
        liquidity_item = QTableWidgetItem("$0")
        liquidity_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        liquidity_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 4, liquidity_item)

        # Threshold
        threshold_text = f"{tracked_token.threshold_value:.2f}"
        threshold_item = QTableWidgetItem(threshold_text)
        threshold_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        threshold_item.setData(Qt.ItemDataRole.UserRole, token.id)
        # Make it visually distinct (editable)
        threshold_item.setForeground(QColor("#14ffec" if self.theme_manager.is_dark_theme() else "#0066cc"))
        self.table.setItem(row, 5, threshold_item)

        # Mode
        mode_text = "%" if tracked_token.threshold_mode == "percentage" else "$"
        mode_item = QTableWidgetItem(mode_text)
        mode_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_item.setData(Qt.ItemDataRole.UserRole, token.id)
        mode_item.setForeground(QColor("#14ffec" if self.theme_manager.is_dark_theme() else "#0066cc"))
        self.table.setItem(row, 6, mode_item)

        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("dangerButton")
        remove_btn.setMinimumWidth(90)
        remove_btn.setToolTip(f"Stop tracking {token.symbol}")
        remove_btn.setProperty("token_id", token.id)
        remove_btn.setProperty("token_symbol", token.symbol)
        remove_btn.clicked.connect(lambda checked, tid=token.id, sym=token.symbol: self.on_remove_clicked(tid, sym))
        self.table.setCellWidget(row, 7, remove_btn)

    @Slot(int, int)
    def on_cell_double_clicked(self, row, col):
        """
        Handle cell double-click event.

        Args:
            row: Row index
            col: Column index
        """
        # Only allow editing threshold and mode columns
        if col not in [5, 6]:
            return

        # Get token info
        symbol_item = self.table.item(row, 0)
        if not symbol_item:
            return

        token_id = symbol_item.data(Qt.ItemDataRole.UserRole)
        token_symbol = symbol_item.text()

        # Get current threshold
        threshold_item = self.table.item(row, 5)
        mode_item = self.table.item(row, 6)

        if not threshold_item or not mode_item:
            return

        current_value = float(threshold_item.text())
        current_mode = "percentage" if mode_item.text() == "%" else "dollar"

        # Show edit dialog
        self.show_edit_dialog(token_id, token_symbol, current_value, current_mode)

    def show_edit_dialog(self, token_id, token_symbol, current_value, current_mode):
        """
        Show threshold edit dialog.

        Args:
            token_id: Token ID
            token_symbol: Token symbol
            current_value: Current threshold value
            current_mode: Current threshold mode
        """
        dialog = ThresholdEditDialog(token_symbol, current_value, current_mode, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_value, new_mode = dialog.get_values()

            # Update via token manager
            success = self.token_manager.update_token_threshold(
                token_id,
                new_value,
                new_mode
            )

            if success:
                # Emit signal
                self.threshold_updated.emit(token_id, new_value, new_mode)

                # Reload table
                self.refresh()

                # Show confirmation
                mode_text = "%" if new_mode == "percentage" else "$"
                QMessageBox.information(
                    self,
                    "Threshold Updated",
                    f"Threshold for {token_symbol} updated to {new_value:.2f}{mode_text}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Update Failed",
                    f"Failed to update threshold for {token_symbol}"
                )

    def on_remove_clicked(self, token_id, token_symbol):
        """
        Handle remove button click.

        Args:
            token_id: Token ID to remove
            token_symbol: Token symbol for confirmation message
        """
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Stop tracking {token_symbol}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove via token manager
            success = self.token_manager.remove_token_from_tracked(token_id)

            if success:
                # Emit signal
                self.token_removed.emit(token_id)

                # Reload table
                self.refresh()

                # Show confirmation
                QMessageBox.information(
                    self,
                    "Token Removed",
                    f"Stopped tracking {token_symbol}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Removal Failed",
                    f"Failed to remove {token_symbol}"
                )

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
        token_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        symbol = self.table.item(row, 0).text()

        # Get current threshold info
        threshold_value = float(self.table.item(row, 5).text())
        threshold_mode = "percentage" if self.table.item(row, 6).text() == "%" else "dollar"

        # Create context menu
        menu = QMenu(self)

        # Edit threshold action
        edit_action = QAction(f"Edit Threshold for '{symbol}'", self)
        edit_action.triggered.connect(lambda: self.on_cell_double_clicked(row, 5))
        menu.addAction(edit_action)

        menu.addSeparator()

        # Remove action
        remove_action = QAction(f"Stop Tracking '{symbol}'", self)
        remove_action.triggered.connect(lambda: self.on_remove_clicked(token_id, symbol))
        menu.addAction(remove_action)

        menu.addSeparator()

        # Copy actions
        copy_symbol_action = QAction("Copy Symbol", self)
        copy_symbol_action.triggered.connect(lambda: self.copy_to_clipboard(symbol))
        menu.addAction(copy_symbol_action)

        copy_threshold_action = QAction("Copy Threshold", self)
        copy_threshold_action.triggered.connect(lambda: self.copy_to_clipboard(f"{threshold_value}"))
        menu.addAction(copy_threshold_action)

        # Show menu
        menu.exec(self.table.viewport().mapToGlobal(position))

    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def refresh(self):
        """
        Refresh the table data.
        """
        self.load_tokens()
