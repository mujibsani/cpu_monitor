import tkinter as tk
from tkinter import ttk
import psutil
import wmi

class RamInfo:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.LabelFrame(root, text="💾 RAM Information", padding=12)
        self.frame.pack(fill='x', padx=10, pady=10)

        self.info_labels = {}
        self.fields = ["Total", "Available", "Used", "Usage Percentage"]

        self.label_font = ("Segoe UI", 10, "bold")
        self.value_font = ("Segoe UI", 10)
        self.value_colors = {
            "Total": "#4B0082",          # Indigo
            "Available": "#008080",      # Teal
            "Used": "#FF8C00",           # DarkOrange
            "Usage Percentage": "#DC143C" # Crimson
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

    def _format_bytes(self, size):
        # Human readable memory size
        for unit in ['B','KB','MB','GB','TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def update_info(self):
        try:
            mem = psutil.virtual_memory()
            self.info_labels["Total"].config(text=self._format_bytes(mem.total))
            self.info_labels["Available"].config(text=self._format_bytes(mem.available))
            self.info_labels["Used"].config(text=self._format_bytes(mem.used))
            self.info_labels["Usage Percentage"].config(text=f"{mem.percent} %")
        except Exception as e:
            err_msg = f"Error fetching RAM info: {e}"
            for label in self.info_labels.values():
                label.config(text=err_msg, foreground="red")

import tkinter as tk
from tkinter import ttk
import wmi

class RamDetailedInfo:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.LabelFrame(root, text="💾 RAM Detailed Information", padding=12)
        self.frame.pack(fill='x', padx=10, pady=10)

        self.text = tk.Text(self.frame, height=10, font=("Segoe UI", 10), bg="#f9f9f9", bd=0)
        self.text.pack(fill='both', padx=5, pady=5)
        self.text.config(state=tk.DISABLED)

        self.refresh_btn = ttk.Button(self.frame, text="🔄 Refresh", command=self.update_info)
        self.refresh_btn.pack(pady=6)

        self.update_info()

    def update_info(self):
        try:
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", tk.END)
            c = wmi.WMI()
            mem_modules = c.Win32_PhysicalMemory()
            if not mem_modules:
                self.text.insert(tk.END, "No RAM info found.", ("error",))
                self.text.config(state=tk.DISABLED)
                return
            for i, mem in enumerate(mem_modules, 1):
                manufacturer = mem.Manufacturer or "Unknown"
                speed = mem.Speed or "Unknown"
                capacity_gb = int(mem.Capacity) // (1024**3) if mem.Capacity else "Unknown"
                part_number = mem.PartNumber.strip() if mem.PartNumber else "Unknown"
                serial_number = mem.SerialNumber.strip() if mem.SerialNumber else "Unknown"
                latency = "N/A"  # Latency not available via WMI
                
                self.text.insert(tk.END, f"Module {i}:\n", "module_title")
                self.text.insert(tk.END, "  Manufacturer: ", "label")
                self.text.insert(tk.END, f"{manufacturer}\n", "value_manufacturer")
                self.text.insert(tk.END, "  Speed: ", "label")
                self.text.insert(tk.END, f"{speed} MHz\n", "value_speed")
                self.text.insert(tk.END, "  Capacity: ", "label")
                self.text.insert(tk.END, f"{capacity_gb} GB\n", "value_capacity")
                self.text.insert(tk.END, "  Part Number: ", "label")
                self.text.insert(tk.END, f"{part_number}\n", "value_part")
                # You can enable serial and latency if you want:
                # self.text.insert(tk.END, "  Serial Number: ", "label")
                # self.text.insert(tk.END, f"{serial_number}\n", "value_serial")
                # self.text.insert(tk.END, "  Latency (CAS): ", "label")
                # self.text.insert(tk.END, f"{latency}\n", "value_latency")
                self.text.insert(tk.END, "-"*40 + "\n", "separator")

            # Configure tags for colors and fonts
            self.text.tag_config("module_title", foreground="#2c3e50", font=("Segoe UI", 11, "bold"))
            self.text.tag_config("label", foreground="#34495e", font=("Segoe UI", 10, "bold"))
            self.text.tag_config("value_manufacturer", foreground="#2980b9")
            self.text.tag_config("value_speed", foreground="#d35400")
            self.text.tag_config("value_capacity", foreground="#27ae60")
            self.text.tag_config("value_part", foreground="#8e44ad")
            self.text.tag_config("separator", foreground="#bdc3c7")
            self.text.tag_config("error", foreground="red")

            self.text.config(state=tk.DISABLED)
        except Exception as e:
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, f"Error fetching RAM details: {e}", ("error",))
            self.text.config(state=tk.DISABLED)
