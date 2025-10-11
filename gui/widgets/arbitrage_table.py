
from tkinter import ttk
from typing import List, Tuple
from config import Config


class ArbitrageTable:
    """Table widget for displaying arbitrage opportunities"""
    
    def __init__(self, parent):
        """
        Initialize arbitrage table
        
        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent
        self._create_table()
    
    def _create_table(self):
        """Create the table structure"""
        # Info label
        info_label = ttk.Label(
            self.parent, 
            text="Profitable arbitrage opportunities (sorted by profit %)", 
            font=("Arial", 10, "bold")
        )
        info_label.pack(pady=10)
        
        # Create frame with scrollbar
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Define columns
        columns = ("Token", "Buy from", "Buy Price", "Sell to", 
                  "Sell Price", "Profit %", "Timestamp")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="tree headings",
            yscrollcommand=scrollbar.set, 
            height=15
        )
        
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("Token", width=100, anchor="center")
        self.tree.column("Buy from", width=120, anchor="center")
        self.tree.column("Buy Price", width=120, anchor="center")
        self.tree.column("Sell to", width=120, anchor="center")
        self.tree.column("Sell Price", width=120, anchor="center")
        self.tree.column("Profit %", width=100, anchor="center")
        self.tree.column("Timestamp", width=180, anchor="center")
        
        # Configure headings
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill="both", expand=True)
        
        # Configure tags for color highlighting
        self.tree.tag_configure("high_profit", background=Config.HIGH_PROFIT_COLOR)
        self.tree.tag_configure("medium_profit", background=Config.MEDIUM_PROFIT_COLOR)
    
    def update_display(self, arbitrage_data: List[Tuple]):
        """
        Update the table with new arbitrage data
        
        Args:
            arbitrage_data: List of tuples containing arbitrage opportunity details
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not arbitrage_data:
            # Show message if no opportunities found
            self.tree.insert("", "end", values=(
                "No arbitrage opportunities found",
                "-", "-", "-", "-", "-", "-"
            ))
            return
        
        # Add new data
        for row in arbitrage_data:
            token, buy_dex, buy_price, sell_dex, sell_price, profit_percent, timestamp = row
            
            # Choose tag based on profit percentage
            tag = self._get_profit_tag(profit_percent)
            
            self.tree.insert("", "end", values=(
                token,
                buy_dex,
                f"${buy_price:.6f}",
                sell_dex,
                f"${sell_price:.6f}",
                f"{profit_percent:.2f}%",
                timestamp
            ), tags=(tag,))
    
    def _get_profit_tag(self, profit_percent: float) -> str:
        """
        Get appropriate tag based on profit percentage
        
        Args:
            profit_percent: Profit percentage
            
        Returns:
            Tag name for color highlighting
        """
        if profit_percent >= Config.HIGH_PROFIT_THRESHOLD:
            return "high_profit"
        elif profit_percent >= Config.MEDIUM_PROFIT_THRESHOLD:
            return "medium_profit"
        else:
            return ""
    
    def clear(self):
        """Clear all items from the table"""
        for item in self.tree.get_children():
            self.tree.delete(item)