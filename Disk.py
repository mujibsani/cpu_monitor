import tkinter as tk
from tkinter import ttk
import wmi
import subprocess
import json

class DiskInfo:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.LabelFrame(root, text="💾 Disk Drives Information", padding=12)
        self.frame.pack(fill='x', padx=10, pady=10)

        self.text = tk.Text(self.frame, height=14, font=("Segoe UI", 10), bg="#f0f4f8", fg="#1a1a1a", bd=0)
        self.text.pack(fill='both', padx=5, pady=5)
        self.text.config(state=tk.DISABLED)

        self.refresh_btn = ttk.Button(self.frame, text="🔄 Refresh", command=self.update_info)
        self.refresh_btn.pack(pady=6)

        self.update_info()

    def get_disk_types(self):
        disk_types = {}
        try:
            cmd = ['powershell', '-Command',
                   "Get-PhysicalDisk | Select-Object FriendlyName, MediaType | ConvertTo-Json"]
            output = subprocess.check_output(cmd, text=True)
            disks = json.loads(output)
            if isinstance(disks, dict):
                disks = [disks]

            for disk in disks:
                name = disk.get("FriendlyName", "").strip()
                media = disk.get("MediaType", "Unknown")
                disk_types[name] = media
        except Exception:
            pass
        return disk_types

    def update_info(self):
        try:
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", tk.END)
            c = wmi.WMI()
            disks = c.Win32_DiskDrive()
            if not disks:
                self.text.insert(tk.END, "No disk drive info found.", ("error",))
                self.text.config(state=tk.DISABLED)
                return

            disk_types = self.get_disk_types()

            for i, disk in enumerate(disks, 1):
                size_gb = int(disk.Size) // (1024**3) if disk.Size else "Unknown"
                model = disk.Model.strip() if disk.Model else 'N/A'
                serial = disk.SerialNumber.strip() if disk.SerialNumber else 'N/A'
                interface = disk.InterfaceType if hasattr(disk, 'InterfaceType') else 'N/A'
                media_type = disk.MediaType if hasattr(disk, 'MediaType') else 'N/A'

                disk_type = "Unknown"
                for friendly_name, media in disk_types.items():
                    if friendly_name.lower() in model.lower():
                        disk_type = media
                        break

                # Insert formatted info with tags for colors
                self.text.insert(tk.END, f"Drive {i}:\n", "drive_title")
                self.text.insert(tk.END, f"  Model: ", "label")
                self.text.insert(tk.END, f"{model}\n", "value_model")
                self.text.insert(tk.END, f"  Serial Number: ", "label")
                self.text.insert(tk.END, f"{serial}\n", "value_serial")
                self.text.insert(tk.END, f"  Interface Type: ", "label")
                self.text.insert(tk.END, f"{interface}\n", "value_interface")
                self.text.insert(tk.END, f"  Size: ", "label")
                self.text.insert(tk.END, f"{size_gb} GB\n", "value_size")
                self.text.insert(tk.END, f"  Media Type (WMI): ", "label")
                self.text.insert(tk.END, f"{media_type}\n", "value_media")
                self.text.insert(tk.END, f"  Drive Type (PowerShell): ", "label")
                self.text.insert(tk.END, f"{disk_type}\n", "value_disk_type")
                self.text.insert(tk.END, "-"*45 + "\n", "separator")

            # Color configuration
            self.text.tag_config("drive_title", foreground="#2c3e50", font=("Segoe UI", 11, "bold"))
            self.text.tag_config("label", foreground="#34495e", font=("Segoe UI", 10, "bold"))
            self.text.tag_config("value_model", foreground="#2980b9")
            self.text.tag_config("value_serial", foreground="#8e44ad")
            self.text.tag_config("value_interface", foreground="#16a085")
            self.text.tag_config("value_size", foreground="#d35400")
            self.text.tag_config("value_media", foreground="#c0392b")
            self.text.tag_config("value_disk_type", foreground="#27ae60")
            self.text.tag_config("separator", foreground="#bdc3c7")

            self.text.config(state=tk.DISABLED)

        except Exception as e:
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, f"Error fetching disk info: {e}", ("error",))
            self.text.tag_config("error", foreground="red")
            self.text.config(state=tk.DISABLED)
