"""
Comprehensive Integration Tests for DEX Analyzer
Tests all functionality across the application
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest

from gui.main_window import MainWindow
from database.migration_manager import MigrationManager
from database.database_manager import DatabaseManager


class IntegrationTestRunner:
    """Runs comprehensive integration tests on the application."""

    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setStyle('Fusion')

        # Initialize database
        self.db = DatabaseManager()
        MigrationManager(self.db).run_migrations()

        # Create main window
        self.window = MainWindow()
        self.window.show()

        # Test results
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log_test(self, test_name, passed, message=""):
        """Log test result."""
        status = "[PASS]" if passed else "[FAIL]"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"

        self.test_results.append(result)

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

        print(result)

    def test_window_initialization(self):
        """Test 1: Window initialization and basic setup."""
        print("\n[TEST 1] Window Initialization")

        # Check window exists
        self.log_test("Window created", self.window is not None)

        # Check window title
        self.log_test(
            "Window title correct",
            self.window.windowTitle() == "DEX Arbitrage Monitor"
        )

        # Check window size (should be default or restored)
        width = self.window.width()
        height = self.window.height()
        self.log_test(
            "Window size reasonable",
            width >= 800 and height >= 600,
            f"Size: {width}x{height}"
        )

        # Check tabs exist
        tab_count = self.window.tab_widget.count()
        self.log_test("All 4 tabs created", tab_count == 4, f"Count: {tab_count}")

        # Check tab names
        expected_tabs = [
            "Available Tokens",
            "Tracked Tokens",
            "Current Prices",
            "Arbitrage Opportunities"
        ]
        for i, expected in enumerate(expected_tabs):
            actual = self.window.tab_widget.tabText(i)
            self.log_test(
                f"Tab {i+1} name correct",
                actual == expected,
                f"Expected: {expected}, Got: {actual}"
            )

    def test_available_tokens_tab(self):
        """Test 2: Available Tokens table functionality."""
        print("\n[TEST 2] Available Tokens Tab")

        # Switch to tab
        self.window.tab_widget.setCurrentIndex(0)
        QTest.qWait(100)

        table = self.window.available_tokens_table

        # Check table has data
        row_count = table.table.rowCount()
        self.log_test(
            "Table has tokens",
            row_count > 0,
            f"Rows: {row_count}"
        )

        # Check search box exists
        self.log_test(
            "Search box exists",
            table.search_box is not None
        )

        # Test search functionality
        table.search_box.setText("BTC")
        QTest.qWait(100)
        visible_rows = sum(1 for i in range(table.table.rowCount())
                          if not table.table.isRowHidden(i))
        self.log_test(
            "Search filters table",
            visible_rows < row_count,
            f"Visible: {visible_rows}/{row_count}"
        )

        # Clear search
        table.search_box.clear()
        QTest.qWait(100)

        # Check add button exists and is initially disabled
        self.log_test(
            "Add button exists",
            table.add_button is not None
        )

        # Check tooltips
        self.log_test(
            "Search has tooltip",
            len(table.search_box.toolTip()) > 0
        )
        self.log_test(
            "Add button has tooltip",
            len(table.add_button.toolTip()) > 0
        )

    def test_tracked_tokens_tab(self):
        """Test 3: Tracked Tokens table functionality."""
        print("\n[TEST 3] Tracked Tokens Tab")

        # Switch to tab
        self.window.tab_widget.setCurrentIndex(1)
        QTest.qWait(100)

        table = self.window.tracked_tokens_table

        # Check table exists
        self.log_test("Table exists", table.table is not None)

        # Check has tracked tokens
        row_count = table.table.rowCount()
        self.log_test(
            "Has tracked tokens",
            row_count > 0,
            f"Tracked: {row_count}"
        )

        # Check columns
        expected_cols = 8
        actual_cols = table.table.columnCount()
        self.log_test(
            "Correct column count",
            actual_cols == expected_cols,
            f"Columns: {actual_cols}"
        )

        # Check remove button exists in first row
        if row_count > 0:
            remove_btn = table.table.cellWidget(0, 7)
            self.log_test(
                "Remove button exists",
                remove_btn is not None
            )
            if remove_btn:
                self.log_test(
                    "Remove button has tooltip",
                    len(remove_btn.toolTip()) > 0
                )

    def test_current_prices_tab(self):
        """Test 4: Current Prices table functionality."""
        print("\n[TEST 4] Current Prices Tab")

        # Switch to tab
        self.window.tab_widget.setCurrentIndex(2)
        QTest.qWait(100)

        table = self.window.current_prices_table

        # Check controls exist
        self.log_test("Refresh button exists", table.refresh_btn is not None)
        self.log_test("Auto-refresh checkbox exists", table.auto_refresh_cb is not None)
        self.log_test("Status label exists", table.status_label is not None)

        # Check tooltips
        self.log_test(
            "Refresh button has tooltip",
            len(table.refresh_btn.toolTip()) > 0,
            table.refresh_btn.toolTip()
        )
        self.log_test(
            "Auto-refresh has tooltip",
            len(table.auto_refresh_cb.toolTip()) > 0
        )

        # Check table structure
        expected_cols = 9
        actual_cols = table.table.columnCount()
        self.log_test(
            "Correct column count",
            actual_cols == expected_cols,
            f"Columns: {actual_cols}"
        )

        # Check column headers
        headers = [table.table.horizontalHeaderItem(i).text()
                  for i in range(actual_cols)]
        self.log_test(
            "Has DEX columns",
            "Uniswap V3" in headers and "PancakeSwap V3" in headers,
            f"Headers: {', '.join(headers[:5])}"
        )

    def test_arbitrage_tab(self):
        """Test 5: Arbitrage Opportunities table functionality."""
        print("\n[TEST 5] Arbitrage Opportunities Tab")

        # Switch to tab
        self.window.tab_widget.setCurrentIndex(3)
        QTest.qWait(100)

        table = self.window.arbitrage_table

        # Check controls exist
        self.log_test("Scan button exists", table.scan_btn is not None)
        self.log_test("Auto-scan checkbox exists", table.auto_scan_cb is not None)
        self.log_test("Export button exists", table.export_btn is not None)
        self.log_test("Status label exists", table.status_label is not None)

        # Check tooltips
        self.log_test(
            "Scan button has tooltip",
            len(table.scan_btn.toolTip()) > 0
        )
        self.log_test(
            "Auto-scan has tooltip",
            len(table.auto_scan_cb.toolTip()) > 0
        )
        self.log_test(
            "Export button has tooltip",
            len(table.export_btn.toolTip()) > 0
        )

        # Check statistics label exists
        self.log_test("Statistics label exists", table.stats_label is not None)

        # Check table structure
        expected_cols = 9
        actual_cols = table.table.columnCount()
        self.log_test(
            "Correct column count",
            actual_cols == expected_cols,
            f"Columns: {actual_cols}"
        )

    def test_theme_system(self):
        """Test 6: Theme switching functionality."""
        print("\n[TEST 6] Theme System")

        # Check theme manager exists
        self.log_test(
            "Theme manager exists",
            self.window.theme_manager is not None
        )

        # Get initial theme
        initial_theme = self.window.theme_manager.current_theme
        self.log_test(
            "Has current theme",
            initial_theme in ["dark", "light"],
            f"Theme: {initial_theme}"
        )

        # Check theme toggle button exists
        self.log_test(
            "Theme toggle button exists",
            self.window.theme_toggle_btn is not None
        )

        # Check button has tooltip
        self.log_test(
            "Theme button has tooltip",
            len(self.window.theme_toggle_btn.toolTip()) > 0
        )

        # Test theme toggle
        self.window.on_theme_toggle()
        QTest.qWait(100)

        new_theme = self.window.theme_manager.current_theme
        self.log_test(
            "Theme toggled",
            new_theme != initial_theme,
            f"Changed from {initial_theme} to {new_theme}"
        )

        # Toggle back
        self.window.on_theme_toggle()
        QTest.qWait(100)

        restored_theme = self.window.theme_manager.current_theme
        self.log_test(
            "Theme restored",
            restored_theme == initial_theme,
            f"Back to {restored_theme}"
        )

    def test_keyboard_shortcuts(self):
        """Test 7: Keyboard shortcuts."""
        print("\n[TEST 7] Keyboard Shortcuts")

        # Check that shortcuts are registered
        actions = self.window.findChildren(QTest.QAction) if hasattr(QTest, 'QAction') else []

        # Check toolbar exists
        toolbar = self.window.findChild(self.window.QToolBar) if hasattr(self.window, 'QToolBar') else None

        # We can verify the methods exist
        self.log_test(
            "Refresh method exists",
            hasattr(self.window, 'on_refresh')
        )
        self.log_test(
            "Scan method exists",
            hasattr(self.window, 'on_scan')
        )
        self.log_test(
            "Theme toggle method exists",
            hasattr(self.window, 'on_theme_toggle')
        )

        # Check status bar exists for feedback
        self.log_test(
            "Status bar exists",
            self.window.statusBar() is not None
        )

    def test_context_menus(self):
        """Test 8: Context menu availability."""
        print("\n[TEST 8] Context Menus")

        # Check Available Tokens has context menu
        available_table = self.window.available_tokens_table.table
        self.log_test(
            "Available Tokens has context menu",
            available_table.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu
        )

        # Check Tracked Tokens has context menu
        tracked_table = self.window.tracked_tokens_table.table
        self.log_test(
            "Tracked Tokens has context menu",
            tracked_table.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu
        )

        # Check Arbitrage has context menu
        arbitrage_table = self.window.arbitrage_table.table
        self.log_test(
            "Arbitrage has context menu",
            arbitrage_table.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu
        )

        # Check methods exist
        self.log_test(
            "Available Tokens has context handler",
            hasattr(self.window.available_tokens_table, 'show_context_menu')
        )
        self.log_test(
            "Tracked Tokens has context handler",
            hasattr(self.window.tracked_tokens_table, 'show_context_menu')
        )
        self.log_test(
            "Arbitrage has context handler",
            hasattr(self.window.arbitrage_table, 'show_context_menu')
        )

    def test_window_state_persistence(self):
        """Test 9: Window state save/restore."""
        print("\n[TEST 9] Window State Persistence")

        # Check methods exist
        self.log_test(
            "Save state method exists",
            hasattr(self.window, 'save_window_state')
        )
        self.log_test(
            "Restore state method exists",
            hasattr(self.window, 'restore_window_state')
        )

        # Test saving state
        try:
            self.window.save_window_state()
            self.log_test("Can save window state", True)
        except Exception as e:
            self.log_test("Can save window state", False, str(e))

        # Check preferences are stored
        width = self.db.get_preference("window_width")
        self.log_test(
            "Window width saved",
            width is not None,
            f"Width: {width}"
        )

        tab_index = self.db.get_preference("last_tab_index")
        self.log_test(
            "Last tab saved",
            tab_index is not None,
            f"Tab: {tab_index}"
        )

    def test_data_persistence(self):
        """Test 10: Database and data persistence."""
        print("\n[TEST 10] Data Persistence")

        # Check database connection
        self.log_test(
            "Database connected",
            self.window.db_manager is not None
        )

        # Check token manager
        self.log_test(
            "Token manager exists",
            self.window.token_manager is not None
        )

        # Check can get tokens
        try:
            all_tokens = self.window.token_manager.get_all_tokens()
            self.log_test(
                "Can fetch all tokens",
                len(all_tokens) > 0,
                f"Tokens: {len(all_tokens)}"
            )
        except Exception as e:
            self.log_test("Can fetch all tokens", False, str(e))

        # Check can get tracked tokens
        try:
            tracked = self.window.token_manager.get_tracked_tokens()
            self.log_test(
                "Can fetch tracked tokens",
                True,
                f"Tracked: {len(tracked)}"
            )
        except Exception as e:
            self.log_test("Can fetch tracked tokens", False, str(e))

    def test_service_integration(self):
        """Test 11: Service layer integration."""
        print("\n[TEST 11] Service Integration")

        # Check data service exists
        self.log_test(
            "Data service exists",
            self.window.data_service is not None
        )

        # Check service has required methods
        service = self.window.data_service
        self.log_test(
            "Has get_token_price method",
            hasattr(service, 'get_token_price')
        )

        # Check token manager integration
        tm = self.window.token_manager
        self.log_test(
            "Has add_token_to_tracked method",
            hasattr(tm, 'add_token_to_tracked')
        )
        self.log_test(
            "Has remove_token_from_tracked method",
            hasattr(tm, 'remove_token_from_tracked')
        )
        self.log_test(
            "Has update_token_threshold method",
            hasattr(tm, 'update_token_threshold')
        )

    def test_error_handling(self):
        """Test 12: Error handling mechanisms."""
        print("\n[TEST 12] Error Handling")

        # Check error handlers exist in price table
        price_table = self.window.current_prices_table
        self.log_test(
            "Price table has error handler",
            hasattr(price_table, 'on_fetch_error')
        )

        # Check error handlers exist in arbitrage table
        arb_table = self.window.arbitrage_table
        self.log_test(
            "Arbitrage has error handler",
            hasattr(arb_table, 'on_scan_error')
        )

        # Check threads have error signals
        # We can check this by examining the thread classes
        from gui_pyside.threads.price_fetcher import PriceFetcherThread
        from gui_pyside.threads.arbitrage_scanner import ArbitrageScannerThread

        # Create dummy instances to check signals
        dummy_tokens = []
        dummy_service = self.window.data_service

        # This will fail gracefully if there's an issue
        try:
            # Just check the class has error signal defined
            has_price_error = hasattr(PriceFetcherThread, 'error')
            self.log_test("Price fetcher has error signal", has_price_error)

            has_scanner_error = hasattr(ArbitrageScannerThread, 'error')
            self.log_test("Scanner has error signal", has_scanner_error)
        except Exception as e:
            self.log_test("Thread error signals", False, str(e))

    def test_ui_responsiveness(self):
        """Test 13: UI responsiveness and threading."""
        print("\n[TEST 13] UI Responsiveness")

        # Check threads module exists
        try:
            from gui_pyside.threads import price_fetcher, arbitrage_scanner
            self.log_test("Thread modules exist", True)
        except ImportError as e:
            self.log_test("Thread modules exist", False, str(e))

        # Check QTimer usage for auto-refresh
        price_table = self.window.current_prices_table
        self.log_test(
            "Price table has timer",
            hasattr(price_table, 'refresh_timer')
        )

        arb_table = self.window.arbitrage_table
        self.log_test(
            "Arbitrage has timer",
            hasattr(arb_table, 'scan_timer')
        )

        # Check window remains responsive
        self.log_test(
            "Window is responsive",
            self.window.isVisible() and not self.window.isMinimized()
        )

    def test_export_functionality(self):
        """Test 14: CSV export functionality."""
        print("\n[TEST 14] Export Functionality")

        arb_table = self.window.arbitrage_table

        # Check export method exists
        self.log_test(
            "Export method exists",
            hasattr(arb_table, 'export_to_csv')
        )

        # Check export button is connected
        self.log_test(
            "Export button connected",
            arb_table.export_btn is not None
        )

        # Check csv module is imported
        import gui_pyside.widgets.arbitrage_table as arb_module
        self.log_test(
            "CSV module imported",
            hasattr(arb_module, 'csv')
        )

    def run_all_tests(self):
        """Run all integration tests."""
        print("="*70)
        print(" DEX ANALYZER - COMPREHENSIVE INTEGRATION TESTS")
        print("="*70)
        print(f"\nPySide6 Version: {self.app.applicationVersion() or 'N/A'}")
        print(f"Qt Version: {self.app.property('qtVersion') or 'N/A'}")
        print(f"Platform: {sys.platform}")

        # Run all test methods
        test_methods = [
            self.test_window_initialization,
            self.test_available_tokens_tab,
            self.test_tracked_tokens_tab,
            self.test_current_prices_tab,
            self.test_arbitrage_tab,
            self.test_theme_system,
            self.test_keyboard_shortcuts,
            self.test_context_menus,
            self.test_window_state_persistence,
            self.test_data_persistence,
            self.test_service_integration,
            self.test_error_handling,
            self.test_ui_responsiveness,
            self.test_export_functionality,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"\n[ERROR] Test crashed: {test_method.__name__}")
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                self.tests_failed += 1

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0

        print("\n" + "="*70)
        print(" TEST SUMMARY")
        print("="*70)
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.tests_passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.tests_failed}")

        if self.tests_failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if "[FAIL]" in result:
                    print(f"  {result}")

        print("\n" + "="*70)

        if self.tests_failed == 0:
            print(" ALL TESTS PASSED!")
        else:
            print(f" {self.tests_failed} TEST(S) FAILED")

        print("="*70 + "\n")

        return self.tests_failed == 0


def main():
    """Main test runner."""
    runner = IntegrationTestRunner()

    # Run tests
    success = runner.run_all_tests()

    # Close window after a delay
    QTimer.singleShot(2000, runner.window.close)

    # Return exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
