# src/worker.py
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt6.QtCore import QThread, pyqtSignal

from .algorithms import ALGORITHMS
from .benchmark import benchmark_point, make_sizes


class BenchmarkWorker(QThread):
	progress = pyqtSignal(int, int)	  # done, total
	completed = pyqtSignal(dict)		 # {method: (ns, means, stds)}
	failed = pyqtSignal(str)

	def __init__(self, methods, sizes, runs):
		super().__init__()
		self.methods, self.sizes, self.runs = methods, sizes, runs
		self._stop = False

	def stop(self):
		self._stop = True

	def run(self):
		results = {}
		total = len(self.methods) * len(self.sizes)
		done = 0
		try:
			for m in self.methods:
				ns, means, stds = [], [], []
				results[m] = (ns, means, stds)
				for n in self.sizes:
					if self._stop:
						self.completed.emit(results)   # partial results
						return
					mean, std = benchmark_point(ALGORITHMS[m], n, self.runs)
					ns.append(n)
					means.append(mean)
					stds.append(std)
					done += 1
					self.progress.emit(done, total)
			self.completed.emit(results)
		except Exception as exc:  # noqa: BLE001
			self.failed.emit(str(exc))
