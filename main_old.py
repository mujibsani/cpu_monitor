import tkinter as tk
from tkinter import ttk
import threading, time, sys
import psutil, platform, hashlib, cpuinfo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil

def run_hashes(count):
    for _ in range(count):
        hashlib.sha256(b"benchmark").hexdigest()

class BenchmarkRunner:
    def __init__(self, result_labels, logical_threads):
        self.result_labels = result_labels
        self.logical_threads = logical_threads

    def run_test(self, threads):
        count = 1000000
        thread_list = []
        start = time.time()
        for _ in range(threads):
            t = threading.Thread(target=run_hashes, args=(count,), daemon=True)
            t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        duration = time.time() - start
        score = round((count * threads) / duration, 2)
        return score, duration

    def start_benchmark(self):
        def task():
            single_score, single_time = self.run_test(1)
            multi_score, multi_time = self.run_test(self.logical_threads)

            self.result_labels['single_time'].config(text=f"{single_time:.2f} s")
            self.result_labels['single_score'].config(text=f"{single_score} hashes/sec")
            self.result_labels['multi_time'].config(text=f"{multi_time:.2f} s")
            self.result_labels['multi_score'].config(text=f"{multi_score} hashes/sec")

        threading.Thread(target=task, daemon=True).start()


class LiveChart:
    def __init__(self, root):
        self.root = root
        self.max_points = 60
        self.cpu_data = [0] * self.max_points

        # Style for progress bars accent color
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("green.Horizontal.TProgressbar", foreground='#4caf50', background='#4caf50', thickness=20)
        style.configure("CoreAvg.Horizontal.TProgressbar", foreground='#2196f3', background='#2196f3', thickness=22)

        # CPU usage graph
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.line1, = self.ax.plot(range(self.max_points), self.cpu_data, label='Total CPU Usage', color='#2196f3')
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, self.max_points - 1)
        self.ax.set_title('CPU Usage Over Time', fontsize=14, fontweight='bold')
        self.ax.set_ylabel('%', fontsize=12)
        self.ax.tick_params(axis='both', which='major', labelsize=10)
        self.ax.legend(loc='upper right', fontsize=10)
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

        self.usage_label = ttk.Label(root, text="Total CPU Usage: 0.0 %", font=("Segoe UI", 12, "bold"), foreground='#2196f3')
        self.usage_label.pack(pady=5)

        # Scrollable frame for cores and threads
        self.core_frame = ttk.Frame(root)
        self.core_frame.pack(fill='both', expand=True, padx=15, pady=15)

        self.canvas_scroll = tk.Canvas(self.core_frame, height=370, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.core_frame, orient="vertical", command=self.canvas_scroll.yview)
        self.scrollable_frame = ttk.Frame(self.canvas_scroll)

        self.scrollable_frame.bind("<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all")))

        self.canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_scroll.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_scroll.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Get CPU counts
        self.physical = psutil.cpu_count(logical=False)
        self.logical = psutil.cpu_count(logical=True)
        self.threads_per_core = self.logical // self.physical if self.physical else 1

        # Store widgets: per core average bar, then thread bars
        self.core_avg_bars = []
        self.core_avg_labels = []
        self.thread_bars = []   # list of lists: thread bars per core
        self.thread_labels = [] # list of lists: thread labels per core

        for core_idx in range(self.physical):
            # Core frame with light background and border
            frame_core = ttk.LabelFrame(self.scrollable_frame, text=f"Core {core_idx + 1}", padding=8)
            frame_core.pack(fill='x', pady=6)

            # Core average usage bar + label
            avg_frame = ttk.Frame(frame_core)
            avg_frame.pack(fill='x', pady=5)
            label_avg = ttk.Label(avg_frame, text="Core Avg:", width=14, font=("Segoe UI", 11, "bold"))
            label_avg.pack(side='left')
            pbar_avg = ttk.Progressbar(avg_frame, length=280, maximum=100, mode='determinate', style="CoreAvg.Horizontal.TProgressbar")
            pbar_avg.pack(side='left', padx=12)
            lbl_avg_val = ttk.Label(avg_frame, text="0.0%", width=6, font=("Segoe UI", 11))
            lbl_avg_val.pack(side='left')

            self.core_avg_bars.append(pbar_avg)
            self.core_avg_labels.append(lbl_avg_val)

            # Thread bars for this core
            thread_bar_list = []
            thread_label_list = []
            for thread_idx in range(self.threads_per_core):
                thread_frame = ttk.Frame(frame_core)
                thread_frame.pack(fill='x', pady=2)
                lbl_thread = ttk.Label(thread_frame, text=f"Thread {thread_idx + 1}:", width=14, font=("Segoe UI", 10))
                lbl_thread.pack(side='left')
                pbar_thread = ttk.Progressbar(thread_frame, length=250, maximum=100, mode='determinate', style="green.Horizontal.TProgressbar")
                pbar_thread.pack(side='left', padx=12)
                lbl_thread_val = ttk.Label(thread_frame, text="0.0%", width=6, font=("Segoe UI", 10))
                lbl_thread_val.pack(side='left')

                thread_bar_list.append(pbar_thread)
                thread_label_list.append(lbl_thread_val)

            self.thread_bars.append(thread_bar_list)
            self.thread_labels.append(thread_label_list)

        psutil.cpu_percent(interval=None)  # init

        self.after_id = None
        self.update_chart()

    def update_chart(self):
        total = psutil.cpu_percent(interval=None)
        per_thread = psutil.cpu_percent(percpu=True)

        self.cpu_data.append(total)
        if len(self.cpu_data) > self.max_points:
            self.cpu_data.pop(0)

        self.line1.set_data(range(len(self.cpu_data)), self.cpu_data)
        self.ax.set_xlim(0, self.max_points - 1)
        self.canvas.draw()
        self.usage_label.config(text=f"Total CPU Usage: {total:.1f} %")

        # Update core averages and threads
        for core_idx in range(self.physical):
            start_idx = core_idx * self.threads_per_core
            end_idx = start_idx + self.threads_per_core
            thread_usages = per_thread[start_idx:end_idx]

            avg_usage = sum(thread_usages) / len(thread_usages)
            self.core_avg_bars[core_idx].config(value=avg_usage)
            self.core_avg_labels[core_idx].config(text=f"{avg_usage:.1f}%")

            for thread_idx, usage in enumerate(thread_usages):
                self.thread_bars[core_idx][thread_idx].config(value=usage)
                self.thread_labels[core_idx][thread_idx].config(text=f"{usage:.1f}%")

        self.after_id = self.root.after(1000, self.update_chart)

    def stop(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None


def run_gui():
    root = tk.Tk()
    root.title("Universal CPU Benchmark & Monitor")
    root.geometry("620x880")
    root.configure(bg="#f9f9f9")

    cpu_name = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown CPU')
    physical = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)

    ttk.Style().configure('TLabel', background="#f9f9f9")
    ttk.Style().configure('TFrame', background="#f9f9f9")
    ttk.Style().configure('TLabelframe', background="#f9f9f9")
    ttk.Style().configure('TLabelframe.Label', background="#f9f9f9", font=("Segoe UI", 12, "bold"))

    ttk.Label(root, text=f"CPU: {cpu_name}", font=("Segoe UI", 13, "bold"), background="#f9f9f9").pack(pady=8)
    ttk.Label(root, text=f"Physical Cores: {physical} | Logical Threads: {logical}", font=("Segoe UI", 11), background="#f9f9f9").pack()
    ttk.Label(root, text="", font=("Segoe UI", 2), background="#f9f9f9").pack()

    # Benchmark UI
    result_labels = {}

    benchmark_runner = BenchmarkRunner(result_labels, logical)

    btn = ttk.Button(root, text="Run CPU Benchmark", command=benchmark_runner.start_benchmark)
    btn.pack(pady=12)

    # Benchmark results frame
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

    ttk.Label(results_frame, text="Score:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky='w', padx=10, pady=6)
    result_labels['single_score'] = ttk.Label(results_frame, text="Not run", font=("Segoe UI", 11))
    result_labels['single_score'].grid(row=2, column=1, padx=10, pady=6)
    result_labels['multi_score'] = ttk.Label(results_frame, text="Not run", font=("Segoe UI", 11))
    result_labels['multi_score'].grid(row=2, column=2, padx=10, pady=6)

    # Live CPU usage chart and core/thread display
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
