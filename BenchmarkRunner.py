import threading
import time
import hashlib

class BenchmarkRunner:
    def __init__(self, result_labels, logical_threads):
        self.result_labels = result_labels
        self.logical_threads = logical_threads

    def run_test(self, threads):
        count = 1000000
        thread_list = []
        start = time.time()
        for _ in range(threads):
            t = threading.Thread(target=self.run_hashes, args=(count,), daemon=True)
            t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        duration = time.time() - start
        score = round((count * threads) / duration, 2)
        return score, duration

    def run_hashes(self, count):
        for _ in range(count):
            hashlib.sha256(b"benchmark").hexdigest()

    def start_benchmark(self, callback=None):
        def task():
            single_score, single_time = self.run_test(1)
            multi_score, multi_time = self.run_test(self.logical_threads)

            self.result_labels['single_time'].config(text=f"{single_time:.2f} s")
            self.result_labels['single_score'].config(text=f"{single_score} ")
            self.result_labels['multi_time'].config(text=f"{multi_time:.2f} s")
            self.result_labels['multi_score'].config(text=f"{multi_score} ")

            if callback:
                callback()

        threading.Thread(target=task, daemon=True).start()
    