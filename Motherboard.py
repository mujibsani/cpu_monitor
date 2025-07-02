import tkinter as tk
from tkinter import ttk
import wmi

class MotherboardInfo:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.LabelFrame(root, text="🖥️ Motherboard Information", padding=12)
        self.frame.pack(fill='x', padx=10, pady=10)

        self.info_labels = {}
        self.fields = ["Manufacturer", "Product Name", "Version", "Serial Number"]

        # Fonts and colors
        self.label_font = ("Segoe UI", 10, "bold")
        self.value_font = ("Segoe UI", 10)
        self.value_colors = {
            "Manufacturer": "#1E90FF",  # DodgerBlue
            "Product Name": "#228B22",  # ForestGreen
            "Version": "#8B4513",       # SaddleBrown
            "Serial Number": "#B22222"  # FireBrick
        }

        for field in self.fields:
            container = ttk.Frame(self.frame)
            container.pack(fill='x', pady=3)

            label = ttk.Label(container, text=f"{field}:", font=self.label_font)
            label.pack(side='left')

            value_label = ttk.Label(container, text="Loading...", font=self.value_font, foreground=self.value_colors.get(field, "black"))
            value_label.pack(side='left', padx=6)
            self.info_labels[field] = value_label

        self.refresh_btn = ttk.Button(self.frame, text="🔄 Refresh", command=self.update_info)
        self.refresh_btn.pack(pady=6)

        self.update_info()

    def update_info(self):
        try:
            c = wmi.WMI()
            boards = c.Win32_BaseBoard()
            if boards:
                board = boards[0]
                self.info_labels["Manufacturer"].config(text=board.Manufacturer or "N/A")
                self.info_labels["Product Name"].config(text=board.Product or "N/A")
                self.info_labels["Version"].config(text=board.Version or "N/A")
                self.info_labels["Serial Number"].config(text=board.SerialNumber or "N/A")
            else:
                for label in self.info_labels.values():
                    label.config(text="No motherboard info found", foreground="red")
        except Exception as e:
            err_msg = f"Error fetching info: {e}"
            for label in self.info_labels.values():
                label.config(text=err_msg, foreground="red")
