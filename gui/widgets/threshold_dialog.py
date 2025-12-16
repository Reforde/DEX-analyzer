"""
Threshold Edit Dialog for DEX Analyzer.
Modal dialog for editing token arbitrage thresholds.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QRadioButton, QPushButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QDoubleValidator


class ThresholdEditDialog(QDialog):
    """
    Dialog for editing token arbitrage threshold and mode.
    """

    def __init__(self, token_symbol, current_value, current_mode, parent=None):
        """
        Initialize threshold edit dialog.

        Args:
            token_symbol: Symbol of the token being edited
            current_value: Current threshold value
            current_mode: Current threshold mode ('percentage' or 'dollar')
            parent: Parent widget
        """
        super().__init__(parent)

        self.token_symbol = token_symbol
        self.current_value = current_value
        self.current_mode = current_mode

        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface.
        """
        self.setWindowTitle(f"Edit Threshold - {self.token_symbol}")
        self.setModal(True)
        self.setFixedSize(450, 250)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(f"<h2>Edit Arbitrage Threshold</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Token info
        info_label = QLabel(f"Token: <b>{self.token_symbol}</b>")
        info_label.setStyleSheet("font-size: 12pt;")
        layout.addWidget(info_label)

        # Threshold value input
        value_layout = QHBoxLayout()
        value_label = QLabel("Threshold Value:")
        value_label.setFixedWidth(130)
        value_layout.addWidget(value_label)

        self.value_input = QLineEdit()
        self.value_input.setText(str(self.current_value))
        self.value_input.setPlaceholderText("Enter threshold value")

        # Set validator for numeric input (0.0 to 1000.0, 2 decimal places)
        validator = QDoubleValidator(0.0, 1000.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        # Use C locale to ensure dot (.) is used as decimal separator
        c_locale = QLocale(QLocale.Language.C)
        validator.setLocale(c_locale)

        self.value_input.setValidator(validator)

        value_layout.addWidget(self.value_input)
        layout.addLayout(value_layout)

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Threshold Mode:")
        mode_label.setFixedWidth(130)
        mode_layout.addWidget(mode_label)

        # Radio buttons for mode
        self.percentage_radio = QRadioButton("Percentage (%)")
        self.dollar_radio = QRadioButton("Dollar ($)")

        # Set current mode
        if self.current_mode == "percentage":
            self.percentage_radio.setChecked(True)
        else:
            self.dollar_radio.setChecked(True)

        # Group radio buttons
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.percentage_radio)
        self.mode_group.addButton(self.dollar_radio)

        mode_layout.addWidget(self.percentage_radio)
        mode_layout.addWidget(self.dollar_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Help text
        help_label = QLabel(
            "<i>Percentage: Profit % of buy price (e.g., 2.5%)<br>"
            "Dollar: Absolute profit in USD (e.g., $10.00)</i>"
        )
        help_label.setStyleSheet("color: #808080; font-size: 9pt;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.setFixedWidth(100)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        # Focus on value input
        self.value_input.setFocus()
        self.value_input.selectAll()

    def validate_and_accept(self):
        """
        Validate input and accept dialog.
        """
        # Check if value is empty
        if not self.value_input.text().strip():
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a threshold value."
            )
            self.value_input.setFocus()
            return

        # Try to parse value
        try:
            value = float(self.value_input.text())
            if value < 0:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Threshold value must be positive."
                )
                self.value_input.setFocus()
                return
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid number."
            )
            self.value_input.setFocus()
            return

        # All validation passed
        self.accept()

    def get_values(self):
        """
        Get the entered threshold values.

        Returns:
            Tuple of (value: float, mode: str)
        """
        value = float(self.value_input.text())
        mode = "percentage" if self.percentage_radio.isChecked() else "dollar"
        return value, mode
