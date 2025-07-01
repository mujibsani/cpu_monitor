import sys
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cpuinfo
import psutil
from BenchmarkRunner import BenchmarkRunner
from LiveChart import LiveChart

# Add this import for GPU monitoring
import GPUtil
import ctypes
from ctypes import wintypes

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
        return False  # Another instance is running

    return True




def run_gui():
    if not check_single_instance():
        messagebox.showwarning("Already Running", "Another instance of this app is already running.")
        sys.exit(0)

    root = tk.Tk()
    root.title("Universal CPU Benchmark & Monitor")
    root.geometry("620x960")  # Increased height to fit GPU section
    root.configure(bg="#f9f9f9")

    cpu_name = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown CPU')
    physical = psutil.cpu_count(logical=False) or 1
    logical = psutil.cpu_count(logical=True) or 1

    ttk.Style().configure('TLabel', background="#f9f9f9")
    ttk.Style().configure('TFrame', background="#f9f9f9")
    ttk.Style().configure('TLabelframe', background="#f9f9f9")
    ttk.Style().configure('TLabelframe.Label', background="#f9f9f9", font=("Segoe UI", 12, "bold"))

    ttk.Label(root, text=f"CPU: {cpu_name}", font=("Segoe UI", 13, "bold"), background="#f9f9f9").pack(pady=8)
    ttk.Label(root, text=f"Physical Cores: {physical} | Logical Threads: {logical}", font=("Segoe UI", 11), background="#f9f9f9").pack()
    ttk.Label(root, text="", font=("Segoe UI", 2), background="#f9f9f9").pack()

    result_labels = {}
    benchmark_runner = BenchmarkRunner(result_labels, logical)

    btn = ttk.Button(root, text="Run CPU Benchmark")
    btn.pack(pady=12)

    status_label = ttk.Label(root, text="", font=("Segoe UI", 10, "italic"), foreground="blue", background="#f9f9f9")
    status_label.pack()

    def on_benchmark_start():
        btn.config(state='disabled')
        status_label.config(text="Running benchmark... Please wait.")

        def finished():
            status_label.config(text="Benchmark complete!")
            btn.config(state='normal')

        benchmark_runner.start_benchmark(callback=finished)

    btn.config(command=on_benchmark_start)

    results_frame = ttk.LabelFrame(root, text="Benchmark Results", padding=12)
    results_frame.pack(fill='x', padx=18, pady=18)

    ttk.Label(results_frame, text="Test", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=10, pady=8)
    ttk.Label(results_frame, text="Single-threaded", font=("Segoe UI", 11, "bold")).grid(row=0, column=1, padx=10, pady=8)
    ttk.Label(results_frame, text="Multi-threaded", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=10, pady=8)

    ttk.Label(results_frame, text="Time:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky='w', padx=10, pady=6)
    result_labels['single_time'] = ttk.Label(results_frame, text="Not run", font=("Segoe UI", 11))
    result_labels['single_time'].grid(row=1, column=1, padx=10, pady=6)
    result_labels['multi_time'] = ttk.Label(results_frame, text="Not run", font=("Segoe UI", 11))
    result_labels['multi_time'].grid(row=1, column=2, padx=10, pady=6)

    ttk.Label(results_frame, text="Score (hashes/sec):", font=("Segoe UI", 11)).grid(row=2, column=0, sticky='w', padx=10, pady=6)
    result_labels['single_score'] = ttk.Label(results_frame, text="Not run", font=("Segoe UI", 11))
    result_labels['single_score'].grid(row=2, column=1, padx=10, pady=6)
    result_labels['multi_score'] = ttk.Label(results_frame, text="Not run", font=("Segoe UI", 11))
    result_labels['multi_score'].grid(row=2, column=2, padx=10, pady=6)
    
    chart = LiveChart(root)


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
