import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

        self.physical = psutil.cpu_count(logical=False)
        self.logical = psutil.cpu_count(logical=True)
        self.threads_per_core = self.logical // self.physical if self.physical else 1

        self.core_avg_bars = []
        self.core_avg_labels = []
        self.thread_bars = []
        self.thread_labels = []

        core_colors = ['#bbdefb', '#c8e6c9']  # alternating light blue and light green

        for core_idx in range(self.physical):
            bg_color = core_colors[core_idx % len(core_colors)]
            frame_core = tk.Frame(self.scrollable_frame, bg=bg_color, bd=2, relief='groove')
            frame_core.pack(fill='x', pady=6, padx=8)

            label_core = tk.Label(frame_core, text=f"🖥️ Core {core_idx + 1}", bg=bg_color,
                                  font=("Segoe UI", 14, "bold"))
            label_core.pack(anchor='w', padx=8, pady=4)

            avg_frame = tk.Frame(frame_core, bg=bg_color)
            avg_frame.pack(fill='x', pady=6, padx=10)

            label_avg = tk.Label(avg_frame, text="Core Avg:", bg=bg_color,
                                 font=("Segoe UI", 12, "bold"), width=12, anchor='w')
            label_avg.pack(side='left')

            pbar_avg = ttk.Progressbar(avg_frame, length=280, maximum=100, mode='determinate',
                                      style="CoreAvg.Horizontal.TProgressbar")
            pbar_avg.pack(side='left', padx=12)

            lbl_avg_val = tk.Label(avg_frame, text="0.0%", bg=bg_color,
                                   font=("Segoe UI", 12), width=6)
            lbl_avg_val.pack(side='left')

            self.core_avg_bars.append(pbar_avg)
            self.core_avg_labels.append(lbl_avg_val)

            thread_bar_list = []
            thread_label_list = []
            for thread_idx in range(self.threads_per_core):
                thread_frame = tk.Frame(frame_core, bg=bg_color)
                thread_frame.pack(fill='x', pady=2, padx=24)

                lbl_thread = tk.Label(thread_frame, text=f"🧵 Thread {thread_idx + 1}:", bg=bg_color,
                                      font=("Segoe UI", 11), width=12, anchor='w')
                lbl_thread.pack(side='left')

                pbar_thread = ttk.Progressbar(thread_frame, length=240, maximum=100, mode='determinate',
                                             style="green.Horizontal.TProgressbar")
                pbar_thread.pack(side='left', padx=10)

                lbl_thread_val = tk.Label(thread_frame, text="0.0%", bg=bg_color,
                                         font=("Segoe UI", 11), width=6)
                lbl_thread_val.pack(side='left')

                thread_bar_list.append(pbar_thread)
                thread_label_list.append(lbl_thread_val)

            self.thread_bars.append(thread_bar_list)
            self.thread_labels.append(thread_label_list)

        psutil.cpu_percent(interval=None)  # initialize stats

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
