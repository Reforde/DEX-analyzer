from gui.main_window import MainWindow
import tkinter as tk


def main():
    """Initialize and run the application"""
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()