
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

from config import Config
from database.database_manager import DatabaseManager
from api.bitquery_client import BitqueryClient
from services.price_fetcher import PriceFetcher
from services.arbitrage_analyzer import ArbitrageAnalyzer
from gui.widgets.price_table import PriceTable
from gui.widgets.arbitrage_table import ArbitrageTable


class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        """
        Initialize main window
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title(Config.WINDOW_TITLE)
        self.root.geometry(Config.WINDOW_SIZE)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.api_client = None
        self.price_fetcher = None
        self.arbitrage_analyzer = None
        
        # Configuration
        self.arbitrage_threshold = Config.DEFAULT_THRESHOLD
        self.auto_refresh = False
        
        # Create GUI
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Configuration frame
        self._create_config_frame()
        
        # Notebook with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Prices tab
        prices_frame = ttk.Frame(notebook)
        notebook.add(prices_frame, text="Current Prices")
        self.price_table = PriceTable(prices_frame)
        
        # Arbitrage tab
        arbitrage_frame = ttk.Frame(notebook)
        notebook.add(arbitrage_frame, text="Arbitrage Opportunities")
        self.arbitrage_table = ArbitrageTable(arbitrage_frame)
    
    def _create_config_frame(self):
        """Create configuration frame with controls"""
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # API Key
        ttk.Label(config_frame, text="Bitquery API Key:").grid(
            row=0, column=0, sticky="w", padx=5)
        self.api_key_entry = ttk.Entry(config_frame, width=60, show="*")
        self.api_key_entry.grid(row=0, column=1, columnspan=2, padx=5, sticky="ew")
        
        # Threshold
        ttk.Label(config_frame, text="Arbitrage Threshold (%):").grid(
            row=1, column=0, sticky="w", padx=5)
        self.threshold_entry = ttk.Entry(config_frame, width=10)
        self.threshold_entry.insert(0, str(Config.DEFAULT_THRESHOLD))
        self.threshold_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Buttons
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        self.fetch_btn = ttk.Button(btn_frame, text="Fetch Prices", 
                                    command=self._on_fetch_prices)
        self.fetch_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Test Connection", 
                  command=self._on_test_connection).pack(side="left", padx=5)
        
        self.auto_refresh_btn = ttk.Button(btn_frame, text="Start Auto-Refresh",
                                          command=self._on_toggle_auto_refresh)
        self.auto_refresh_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Clear Database",
                  command=self._on_clear_database).pack(side="left", padx=5)
        
        # Status label
        self.status_label = ttk.Label(config_frame, text="Status: Ready", 
                                     foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=3, pady=5)
    
    def _initialize_services(self) -> bool:
        """
        Initialize API client and services
        
        Returns:
            True if successful, False otherwise
        """
        api_key = self.api_key_entry.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter your Bitquery API key")
            return False
        
        try:
            threshold = float(self.threshold_entry.get())
            self.arbitrage_threshold = threshold
        except ValueError:
            messagebox.showerror("Error", "Invalid threshold value")
            return False
        
        # Initialize services
        self.api_client = BitqueryClient(api_key)
        self.price_fetcher = PriceFetcher(self.api_client)
        self.arbitrage_analyzer = ArbitrageAnalyzer(self.db_manager, threshold)
        
        return True
    
    def _on_test_connection(self):
        """Handle test connection button click"""
        if not self._initialize_services():
            return
        
        thread = threading.Thread(target=self._test_connection_worker, daemon=True)
        thread.start()
    
    def _test_connection_worker(self):
        """Worker thread for testing connection"""
        self._update_status("Testing connection...", "orange")
        
        result = self.api_client.test_connection()
        
        if result["success"]:
            self._update_status("Connection successful!", "green")
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", "Successfully connected to Bitquery API!\n\nYou can now fetch prices."))
        else:
            self._update_status(f"Connection failed: {result['message']}", "red")
            self.root.after(0, lambda: messagebox.showerror(
                "Connection Failed", f"Failed to connect:\n{result['message']}"))
    
    def _on_fetch_prices(self):
        """Handle fetch prices button click"""
        if not self._initialize_services():
            return
        
        thread = threading.Thread(target=self._fetch_prices_worker, daemon=True)
        thread.start()
    
    def _fetch_prices_worker(self):
        """Worker thread for fetching prices"""
        self._update_status("Fetching prices...", "orange")
        self.fetch_btn.config(state="disabled")
        
        try:
            timestamp = datetime.now()
            
            # Fetch all prices
            price_results = self.price_fetcher.fetch_all_prices(
                Config.SUPPORTED_DEXES,
                Config.SUPPORTED_TOKENS,
                Config.BASE_CURRENCY
            )
            
            # Store prices in database
            success_count = 0
            for dex, tokens in price_results.items():
                for token, data in tokens.items():
                    self.db_manager.insert_price(
                        timestamp=timestamp,
                        dex=dex,
                        token=token,
                        base_currency=Config.BASE_CURRENCY,
                        price=data['price'],
                        volume=data['volume']
                    )
                    success_count += 1
            
            if success_count == 0:
                raise Exception("No data was fetched successfully.")
            
            # Find arbitrage opportunities
            opportunities = self.arbitrage_analyzer.find_opportunities(
                timestamp=timestamp,
                tokens=Config.SUPPORTED_TOKENS,
                dexes=Config.SUPPORTED_DEXES
            )
            
            # Save opportunities
            self.arbitrage_analyzer.save_opportunities(opportunities, timestamp)
            
            # Update GUI
            self.root.after(0, self._update_displays)
            
            self._update_status(
                f"Prices updated successfully ({success_count} pairs fetched)", "green")
        
        except Exception as e:
            self._update_status(f"Error: {str(e)}", "red")
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Failed to fetch prices:\n{str(e)}"))
        
        finally:
            self.fetch_btn.config(state="normal")
    
    def _update_displays(self):
        """Update both price and arbitrage displays"""
        self.price_table.update_display(self.db_manager.get_latest_prices())
        self.arbitrage_table.update_display(
            self.db_manager.get_latest_arbitrage_opportunities())
    
    def _on_toggle_auto_refresh(self):
        """Handle auto-refresh toggle"""
        self.auto_refresh = not self.auto_refresh
        
        if self.auto_refresh:
            if not self._initialize_services():
                self.auto_refresh = False
                return
            
            self.auto_refresh_btn.config(text="Stop Auto-Refresh")
            thread = threading.Thread(target=self._auto_refresh_worker, daemon=True)
            thread.start()
        else:
            self.auto_refresh_btn.config(text="Start Auto-Refresh")
    
    def _auto_refresh_worker(self):
        """Worker thread for auto-refresh"""
        while self.auto_refresh:
            self._fetch_prices_worker()
            time.sleep(Config.AUTO_REFRESH_INTERVAL)
    
    def _on_clear_database(self):
        """Handle clear database button click"""
        response = messagebox.askyesno(
            "Confirm", "Are you sure you want to clear all data?")
        
        if response:
            self.db_manager.clear_all_data()
            self._update_displays()
            messagebox.showinfo("Success", "Database cleared successfully")
    
    def _update_status(self, message: str, color: str):
        """
        Update status label
        
        Args:
            message: Status message
            color: Text color
        """
        def update():
            self.status_label.config(text=f"Status: {message}", foreground=color)
        self.root.after(0, update)
    
    def on_closing(self):
        """Handle window closing"""
        self.auto_refresh = False
        self.db_manager.close()
        self.root.destroy()