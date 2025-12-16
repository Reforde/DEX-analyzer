"""
Available Tokens Table widget for DEX Analyzer.
Displays all available tokens with checkboxes for selection.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QPushButton, QLabel, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QAction


class AvailableTokensTable(QWidget):
    """
    Table widget showing available tokens that can be added to tracking.
    """

    # Signal emitted when user wants to add selected tokens
    tokens_added = Signal(list)  # List of token IDs

    def __init__(self, token_manager, theme_manager, parent=None):
        """
        Initialize available tokens table.

        Args:
            token_manager: TokenManager instance for data access
            theme_manager: ThemeManager instance for theming
            parent: Parent widget
        """
        super().__init__(parent)

        self.token_manager = token_manager
        self.theme_manager = theme_manager
        self.selected_tokens = set()  # Set of selected token IDs
        self.all_tokens = []  # All available tokens

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
        title_label = QLabel("Available Tokens")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Select tokens to track")
        subtitle_label.setStyleSheet("color: #808080;")
        header_layout.addWidget(subtitle_label)

        header_layout.addStretch()

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tokens...")
        self.search_box.setFixedWidth(300)
        self.search_box.setToolTip("Search by token symbol or name")
        self.search_box.textChanged.connect(self.filter_table)
        header_layout.addWidget(self.search_box)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "", "Symbol", "Token Name", "Price (USD)", "24H Volume", "Liquidity"
        ])

        # Configure table
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove focus rectangle

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 50)  # Checkbox column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 100)  # Symbol column
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Name stretches
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 120)  # Price column
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 150)  # Volume column
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 150)  # Liquidity column

        # Connect item clicked signal for better checkbox handling
        self.table.itemClicked.connect(self.on_item_clicked)

        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # Footer section
        footer_layout = QHBoxLayout()

        # Selection count
        self.selection_label = QLabel("Selected: 0")
        self.selection_label.setStyleSheet("font-weight: bold;")
        footer_layout.addWidget(self.selection_label)

        footer_layout.addStretch()

        # Info label
        info_label = QLabel("Click checkbox to select tokens, then click 'Add Selected to Tracked'")
        info_label.setStyleSheet("color: #808080; font-style: italic;")
        footer_layout.addWidget(info_label)

        footer_layout.addStretch()

        # Add button
        self.add_button = QPushButton("Add Selected to Tracked")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setFixedWidth(200)
        self.add_button.setToolTip("Add selected tokens to tracked list with default threshold")
        self.add_button.clicked.connect(self.on_add_selected)
        self.add_button.setEnabled(False)
        footer_layout.addWidget(self.add_button)

        layout.addLayout(footer_layout)

    def create_checkbox_item(self, token_id, checked=False):
        """
        Create a checkbox table item.

        Args:
            token_id: Token ID to store
            checked: Whether checkbox is checked

        Returns:
            QTableWidgetItem with checkbox
        """
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        item.setData(Qt.ItemDataRole.UserRole, token_id)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def load_tokens(self):
        """
        Load available tokens from database.
        """
        # Get available (non-tracked) tokens
        self.all_tokens = self.token_manager.get_available_tokens()

        # Clear table
        self.table.setRowCount(0)
        self.selected_tokens.clear()

        # Populate table
        for token in self.all_tokens:
            self.add_token_row(token)

        # Update selection count
        self.update_selection_count()

    def add_token_row(self, token):
        """
        Add a token row to the table.

        Args:
            token: Token object
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Checkbox
        checkbox_item = self.create_checkbox_item(token.id, False)
        self.table.setItem(row, 0, checkbox_item)

        # Symbol
        symbol_item = QTableWidgetItem(token.symbol)
        symbol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 1, symbol_item)

        # Name
        name_item = QTableWidgetItem(token.name)
        name_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 2, name_item)

        # Price (placeholder - will be updated later)
        price_item = QTableWidgetItem("$0.00")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 3, price_item)

        # Volume (placeholder)
        volume_item = QTableWidgetItem("$0")
        volume_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        volume_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 4, volume_item)

        # Liquidity (placeholder)
        liquidity_item = QTableWidgetItem("$0")
        liquidity_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        liquidity_item.setData(Qt.ItemDataRole.UserRole, token.id)
        self.table.setItem(row, 5, liquidity_item)

    @Slot(QTableWidgetItem)
    def on_item_clicked(self, item):
        """
        Handle item click event.

        Args:
            item: The clicked QTableWidgetItem
        """
        if not item:
            return

        # Get the row and column that was clicked
        row = item.row()
        col = item.column()

        # Get checkbox item
        checkbox_item = self.table.item(row, 0)
        if not checkbox_item:
            return

        # If user clicked directly on checkbox column, Qt handles the toggle automatically
        # We just need to update our selected_tokens set
        if col == 0:
            # Checkbox was clicked directly - just sync our state
            token_id = checkbox_item.data(Qt.ItemDataRole.UserRole)
            if checkbox_item.checkState() == Qt.CheckState.Checked:
                self.selected_tokens.add(token_id)
            else:
                self.selected_tokens.discard(token_id)
            self.update_selection_count()
        else:
            # User clicked on other columns - toggle checkbox programmatically
            current_state = checkbox_item.checkState()
            new_state = Qt.CheckState.Unchecked if current_state == Qt.CheckState.Checked else Qt.CheckState.Checked
            checkbox_item.setCheckState(new_state)

            # Update selected tokens set
            token_id = checkbox_item.data(Qt.ItemDataRole.UserRole)
            if new_state == Qt.CheckState.Checked:
                self.selected_tokens.add(token_id)
            else:
                self.selected_tokens.discard(token_id)

            # Update UI
            self.update_selection_count()

    def update_selection_count(self):
        """
        Update selection count label and button state.
        """
        count = len(self.selected_tokens)
        self.selection_label.setText(f"Selected: {count}")
        self.add_button.setEnabled(count > 0)

    @Slot(str)
    def filter_table(self, search_text):
        """
        Filter table rows based on search text.

        Args:
            search_text: Text to search for
        """
        search_text = search_text.lower()

        for row in range(self.table.rowCount()):
            symbol_item = self.table.item(row, 1)
            name_item = self.table.item(row, 2)

            if symbol_item and name_item:
                symbol = symbol_item.text().lower()
                name = name_item.text().lower()

                # Show row if search text matches symbol or name
                match = search_text in symbol or search_text in name
                self.table.setRowHidden(row, not match)

    @Slot()
    def on_add_selected(self):
        """
        Handle 'Add Selected to Tracked' button click.
        """
        if not self.selected_tokens:
            return

        try:
            # Default threshold
            default_threshold = 2.0
            default_mode = "percentage"

            # Add each selected token to tracked
            added_count = 0
            for token_id in self.selected_tokens:
                success = self.token_manager.add_token_to_tracked(
                    token_id,
                    default_threshold,
                    default_mode
                )
                if success:
                    added_count += 1

            # Show success message
            if added_count > 0:
                QMessageBox.information(
                    self,
                    "Tokens Added",
                    f"Successfully added {added_count} token(s) to tracking with default threshold of {default_threshold}%"
                )

                # Emit signal
                self.tokens_added.emit(list(self.selected_tokens))

                # Reload table to remove tracked tokens from available list
                self.load_tokens()
            else:
                QMessageBox.warning(
                    self,
                    "No Tokens Added",
                    "Could not add any tokens. They may already be tracked."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add tokens: {str(e)}"
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
        symbol = self.table.item(row, 1).text()
        name = self.table.item(row, 2).text()

        # Create context menu
        menu = QMenu(self)

        # Toggle selection action
        checkbox_item = self.table.item(row, 0)
        is_checked = checkbox_item.checkState() == Qt.CheckState.Checked

        toggle_action = QAction("Unselect" if is_checked else "Select", self)
        toggle_action.triggered.connect(lambda: self.toggle_token_selection(row))
        menu.addAction(toggle_action)

        menu.addSeparator()

        # Add to tracked action
        add_action = QAction(f"Add '{symbol}' to Tracked", self)
        add_action.triggered.connect(lambda: self.add_single_token(token_id))
        menu.addAction(add_action)

        menu.addSeparator()

        # Copy actions
        copy_symbol_action = QAction("Copy Symbol", self)
        copy_symbol_action.triggered.connect(lambda: self.copy_to_clipboard(symbol))
        menu.addAction(copy_symbol_action)

        copy_name_action = QAction("Copy Name", self)
        copy_name_action.triggered.connect(lambda: self.copy_to_clipboard(name))
        menu.addAction(copy_name_action)

        # Show menu
        menu.exec(self.table.viewport().mapToGlobal(position))

    def toggle_token_selection(self, row):
        """Toggle selection for a token."""
        checkbox_item = self.table.item(row, 0)
        if checkbox_item:
            current_state = checkbox_item.checkState()
            new_state = Qt.CheckState.Unchecked if current_state == Qt.CheckState.Checked else Qt.CheckState.Checked
            checkbox_item.setCheckState(new_state)

            token_id = checkbox_item.data(Qt.ItemDataRole.UserRole)
            if new_state == Qt.CheckState.Checked:
                self.selected_tokens.add(token_id)
            else:
                self.selected_tokens.discard(token_id)

            self.update_selection_count()

    def add_single_token(self, token_id):
        """Add a single token to tracked list."""
        try:
            default_threshold = 2.0
            default_mode = "percentage"

            success = self.token_manager.add_token_to_tracked(
                token_id,
                default_threshold,
                default_mode
            )

            if success:
                QMessageBox.information(
                    self,
                    "Token Added",
                    f"Successfully added token to tracking with default threshold of {default_threshold}%"
                )
                self.tokens_added.emit([token_id])
                self.load_tokens()
            else:
                QMessageBox.warning(
                    self,
                    "Already Tracked",
                    "This token is already being tracked."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add token: {str(e)}"
            )

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
