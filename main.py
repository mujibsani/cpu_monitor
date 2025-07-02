import sys
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import cpuinfo
import psutil
from BenchmarkRunner import BenchmarkRunner
from LiveChart import LiveChart
from Motherboard import MotherboardInfo
import ctypes
from ctypes import wintypes
from Ram import RamInfo, RamDetailedInfo
from Disk import DiskInfo


def check_single_instance():
    mutex_name = "cpu_benchmark_unique_mutex_12345"
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    CreateMutex = kernel32.CreateMutexW
    CreateMutex.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    CreateMutex.restype = wintypes.HANDLE

    GetLastError = kernel32.GetLastError
    GetLastError.restype = wintypes.DWORD

    mutex = CreateMutex(None, False, mutex_name)
    ERROR_ALREADY_EXISTS = 183

    if GetLastError() == ERROR_ALREADY_EXISTS:
        return False
    return True


def run_gui():
    if not check_single_instance():
        messagebox.showwarning("Already Running", "Another instance of this app is already running.")
        sys.exit(0)

    root = tk.Tk()
    root.title("Universal CPU Benchmark & Monitor")
    root.geometry("640x720")
    root.configure(bg="#f9f9f9")

    # Scrollable layout
    canvas = tk.Canvas(root, bg="#f9f9f9", highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure('TLabel', background="#f9f9f9")
    style.configure('TFrame', background="#f9f9f9")
    style.configure('TLabelframe', background="#f9f9f9", borderwidth=2, relief="ridge")
    style.configure('TLabelframe.Label', background="#f9f9f9", font=("Segoe UI", 12, "bold"))

    cpu_name = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown CPU')
    physical = psutil.cpu_count(logical=False) or 1
    logical = psutil.cpu_count(logical=True) or 1

    ttk.Label(scrollable_frame, text=f"🧠 CPU: {cpu_name}", font=("Segoe UI", 13, "bold")).pack(pady=8)
    ttk.Label(scrollable_frame, text=f"🧩 Physical Cores: {physical} | Threads: {logical}",
              font=("Segoe UI", 11)).pack()
    ttk.Label(scrollable_frame, text="").pack()

    # Benchmark section
    result_labels = {}
    benchmark_runner = BenchmarkRunner(result_labels, logical)

    btn = ttk.Button(scrollable_frame, text="▶ Run CPU Benchmark")
    btn.pack(pady=12)

    status_label = ttk.Label(scrollable_frame, text="", font=("Segoe UI", 10, "italic"), foreground="blue")
    status_label.pack()

    def on_benchmark_start():
        btn.config(state='disabled')
        status_label.config(text="Running benchmark... Please wait.")

        def finished():
            status_label.config(text="✅ Benchmark complete!")
            btn.config(state='normal')

        benchmark_runner.start_benchmark(callback=finished)

    btn.config(command=on_benchmark_start)

    # Colorful Benchmark Results section
    results_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ CPU Benchmark Results", padding=12)
    results_frame.pack(fill='x', padx=18, pady=20)

    header_font = ("Segoe UI", 11, "bold")
    label_font = ("Segoe UI", 11)

    ttk.Label(results_frame, text="Test", font=header_font).grid(row=0, column=0, padx=10, pady=8)
    ttk.Label(results_frame, text="Single-threaded", font=header_font).grid(row=0, column=1, padx=10, pady=8)
    ttk.Label(results_frame, text="Multi-threaded", font=header_font).grid(row=0, column=2, padx=10, pady=8)

    ttk.Label(results_frame, text="Time:", font=label_font).grid(row=1, column=0, sticky='w', padx=10, pady=6)
    result_labels['single_time'] = ttk.Label(results_frame, text="Not run", font=label_font, foreground="#FF5722")
    result_labels['single_time'].grid(row=1, column=1, padx=10, pady=6)
    result_labels['multi_time'] = ttk.Label(results_frame, text="Not run", font=label_font, foreground="#4CAF50")
    result_labels['multi_time'].grid(row=1, column=2, padx=10, pady=6)

    ttk.Label(results_frame, text="Score (hashes/sec):", font=label_font).grid(row=2, column=0, sticky='w', padx=10, pady=6)
    result_labels['single_score'] = ttk.Label(results_frame, text="Not run", font=label_font, foreground="#03A9F4")
    result_labels['single_score'].grid(row=2, column=1, padx=10, pady=6)
    result_labels['multi_score'] = ttk.Label(results_frame, text="Not run", font=label_font, foreground="#8BC34A")
    result_labels['multi_score'].grid(row=2, column=2, padx=10, pady=6)

    # Motherboard info (now styled)
    mb_info = MotherboardInfo(scrollable_frame)
    
    # Add below motherboard info in your GUI setup
    ram_info = RamInfo(scrollable_frame)
    
    # inside your GUI code, add
    ram_details = RamDetailedInfo(scrollable_frame)
    
    #Disk Information
    disk_info = DiskInfo(scrollable_frame)
    

    
    # Live chart for CPU usage
    chart = LiveChart(scrollable_frame)

    
    
    def on_close():
        chart.stop()

        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    if platform.system() != "Windows":
        print("This app is for Windows only.")
    else:
        run_gui()
