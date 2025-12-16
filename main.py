"""
Main entry point for DEX Analyzer.

DEX Arbitrage Monitor built with PySide6 (Qt 6).
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.main_window import MainWindow
from database.migration_manager import MigrationManager
from database.database_manager import DatabaseManager


def main():
    """
    Main application entry point.
    """
    # Create Qt Application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("DEX Arbitrage Monitor")
    app.setOrganizationName("DEX Analyzer")
    app.setApplicationVersion("2.0.0")

    # Set global application style
    app.setStyle('Fusion')

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    try:
        # Initialize database
        db_manager = DatabaseManager()

        # Run database migrations
        print("Running database migrations...")
        migration_manager = MigrationManager(db_manager)
        migration_manager.run_migrations()
        print("Database initialized successfully.")

        # Create and show main window
        print("Launching DEX Analyzer...")
        window = MainWindow()
        window.show()

        # Start event loop
        sys.exit(app.exec())

    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
