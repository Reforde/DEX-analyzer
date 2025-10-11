
from tkinter import ttk
from typing import List, Tuple


class PriceTable:
    """Table widget for displaying current prices"""
    
    def __init__(self, parent):
        """
        Initialize price table
        
        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent
        self._create_table()
    
    def _create_table(self):
        """Create the table structure"""
        # Create frame with scrollbar
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Define columns
        columns = ("DEX", "Token", "Price (USDT)", "Volume", "Last Updated")
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
        self.tree.column("DEX", width=150, anchor="center")
        self.tree.column("Token", width=100, anchor="center")
        self.tree.column("Price (USDT)", width=150, anchor="center")
        self.tree.column("Volume", width=200, anchor="center")
        self.tree.column("Last Updated", width=200, anchor="center")
        
        # Configure headings
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill="both", expand=True)
    
    def update_display(self, price_data: List[Tuple]):
        """
        Update the table with new price data
        
        Args:
            price_data: List of tuples containing (dex, token, price, volume, timestamp)
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new data
        for row in price_data:
            dex, token, price, volume, timestamp = row
            self.tree.insert("", "end", values=(
                dex,
                token,
                f"${price:.6f}",
                f"${volume:,.2f}",
                timestamp
            ))
    
    def clear(self):
        """Clear all items from the table"""
        for item in self.tree.get_children():
            self.tree.delete(item)