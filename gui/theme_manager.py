"""
Theme manager for DEX Analyzer.
Handles loading and switching between dark and light themes.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal

from gui.styles.theme_colors import get_theme_colors


class ThemeManager(QObject):
    """
    Manages application themes (dark/light) using QSS stylesheets.
    """

    theme_changed = Signal(str)  # Emits theme name when changed

    def __init__(self, app: QApplication, db_manager=None):
        """
        Initialize theme manager.

        Args:
            app: QApplication instance
            db_manager: Database manager for persisting theme preference (optional)
        """
        super().__init__()
        self.app = app
        self.db_manager = db_manager
        self.current_theme = "dark"  # Default theme

        # Get path to styles directory
        self.styles_dir = Path(__file__).parent / "styles"

        # Load saved theme preference if database manager is available
        if self.db_manager:
            saved_theme = self.db_manager.get_preference("theme", "dark")
            self.current_theme = saved_theme

    def get_qss_path(self, theme_name: str) -> Path:
        """
        Get path to QSS file for specified theme.

        Args:
            theme_name: Either 'dark' or 'light'

        Returns:
            Path to QSS file
        """
        qss_file = f"{theme_name}_theme.qss"
        return self.styles_dir / qss_file

    def load_qss(self, theme_name: str) -> str:
        """
        Load QSS stylesheet content from file.

        Args:
            theme_name: Either 'dark' or 'light'

        Returns:
            QSS stylesheet content as string
        """
        qss_path = self.get_qss_path(theme_name)

        try:
            with open(qss_path, 'r', encoding='utf-8') as f:
                qss_content = f.read()
            return qss_content
        except FileNotFoundError:
            print(f"Warning: Theme file not found: {qss_path}")
            return ""
        except Exception as e:
            print(f"Error loading theme file: {e}")
            return ""

    def apply_theme(self, theme_name: str):
        """
        Apply theme to the application.

        Args:
            theme_name: Either 'dark' or 'light'
        """
        # Normalize theme name
        theme_name = theme_name.lower()
        if theme_name not in ['dark', 'light']:
            print(f"Warning: Unknown theme '{theme_name}', defaulting to 'dark'")
            theme_name = 'dark'

        # Load and apply QSS
        qss = self.load_qss(theme_name)
        if qss:
            self.app.setStyleSheet(qss)
            self.current_theme = theme_name

            # Save preference to database
            if self.db_manager:
                self.db_manager.set_preference("theme", theme_name)

            # Emit signal that theme changed
            self.theme_changed.emit(theme_name)

            print(f"Theme applied: {theme_name}")
        else:
            print(f"Failed to apply theme: {theme_name}")

    def toggle_theme(self) -> str:
        """
        Toggle between dark and light themes.

        Returns:
            New theme name
        """
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme

    def get_current_theme(self) -> str:
        """
        Get currently active theme name.

        Returns:
            Theme name ('dark' or 'light')
        """
        return self.current_theme

    def get_theme_colors(self) -> dict:
        """
        Get color dictionary for current theme.

        Returns:
            Dictionary of color values
        """
        return get_theme_colors(self.current_theme)

    def is_dark_theme(self) -> bool:
        """
        Check if current theme is dark.

        Returns:
            True if dark theme is active
        """
        return self.current_theme == "dark"

    def is_light_theme(self) -> bool:
        """
        Check if current theme is light.

        Returns:
            True if light theme is active
        """
        return self.current_theme == "light"
