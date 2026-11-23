# src/worker.py
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait

from PyQt6.QtCore import QThread, pyqtSignal

from .algorithms import ALGORITHMS
from .benchmark import benchmark_point


def _compute(method: str, n: int, runs: int) -> tuple[str, int, float, float]:
    """
    Runs in a worker process. Must be a top-level function (picklable).
    """
    mean, std = benchmark_point(ALGORITHMS[method], n, runs)
    return method, n, mean, std


class BenchmarkWorker(QThread):
    progress = pyqtSignal(int, int)             # done, total
    point = pyqtSignal(str, int, float, float)  # method, N, mean, std
    completed = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, methods, sizes, runs):
        super().__init__()
        self.methods, self.sizes, self.runs = methods, sizes, runs
        self._stop = False

    @property
    def stopped(self) -> bool:
        return self._stop

    def stop(self):
        self._stop = True

    def run(self):
        # N outer, methods inner: points are submitted left to right
        tasks = [(m, n) for n in self.sizes for m in self.methods]
        total, done = len(tasks), 0
        pool = ProcessPoolExecutor()
        try:
            pending = {pool.submit(_compute, m, n, self.runs) for m, n in tasks}
            while pending and not self._stop:
                finished, pending = wait(pending, timeout=0.1,
                                         return_when=FIRST_COMPLETED)
                for fut in finished:
                    self.point.emit(*fut.result())   # re-raises worker exceptions
                    done += 1
                    self.progress.emit(done, total)
            if self._stop:
                self._kill(pool)
            self.completed.emit()
        except Exception as exc:  # noqa: BLE001
            self._kill(pool)
            self.failed.emit(str(exc))
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

    @staticmethod
    def _kill(pool: ProcessPoolExecutor):
        """Stop points that are still being computed, so Stop is immediate."""
        pool.shutdown(wait=False, cancel_futures=True)
        for p in list(getattr(pool, "_processes", {}).values()):   # private API
            p.terminate()