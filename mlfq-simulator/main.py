import tkinter as tk
import sys
import os

# Ensure Python recognizes `mlfq-simulator` as a package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from .controllers.app import App

if __name__ == "__main__":
    root = tk.Tk()
    app_instance = App(root)
    root.mainloop()