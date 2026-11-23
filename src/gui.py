# src/gui.py
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
	QComboBox, QFormLayout, QHBoxLayout, QLabel, QListWidget,
	QListWidgetItem, QMainWindow, QMessageBox, QProgressBar, QPushButton,
	QSpinBox, QVBoxLayout, QWidget,
)

from src.worker import BenchmarkWorker

from .algorithms import ALGORITHMS
from .benchmark import benchmark_point, make_sizes


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("push_swap benchmark")
		self.results: dict = {}
		self.worker: BenchmarkWorker | None = None

		# --- controls ---
		self.n_start = self._spin(1, 1_000_000, 10)
		self.n_end = self._spin(1, 1_000_000, 500)
		self.n_points = self._spin(1, 10_000, 20)
		self.runs = self._spin(1, 100_000, 20)

		self.n_spacing = QComboBox()
		self.n_spacing.addItems(["linear", "log"])
	
		self.x_scale = QComboBox()
		self.x_scale.addItems(["linear", "log"])
		self.y_scale = QComboBox()
		self.y_scale.addItems(["linear", "log"])
		self.x_scale.currentIndexChanged.connect(self.plot)
		self.y_scale.currentIndexChanged.connect(self.plot)

		self.methods = QListWidget()
		for i, name in enumerate(ALGORITHMS):
			item = QListWidgetItem(name)
			item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
			item.setCheckState(Qt.CheckState.Checked if i == 0 else Qt.CheckState.Unchecked)
			self.methods.addItem(item)
		self.methods.setMaximumHeight(110)

		self.run_btn = QPushButton("Benchmark")
		self.run_btn.clicked.connect(self.start_benchmark)
		self.stop_btn = QPushButton("Stop")
		self.stop_btn.setEnabled(False)
		self.stop_btn.clicked.connect(self.stop_benchmark)
		self.progress = QProgressBar()
		self.status = QLabel("")

		form = QFormLayout()
		form.addRow("N start", self.n_start)
		form.addRow("N end", self.n_end)
		form.addRow("N points", self.n_points)
		form.addRow("N spacing", self.n_spacing)
		form.addRow("Runs per N", self.runs)
		form.addRow("X scale", self.x_scale)
		form.addRow("Y scale", self.y_scale)
		form.addRow("Methods", self.methods)
		buttons = QHBoxLayout()
		buttons.addWidget(self.run_btn)
		buttons.addWidget(self.stop_btn)
		form.addRow(buttons)
		form.addRow(self.progress)
		form.addRow(self.status)

		left = QWidget()
		left.setLayout(form)
		left.setFixedWidth(260)

		# --- plot ---
		self.fig = Figure(layout="constrained")
		self.ax_mean, self.ax_std = self.fig.subplots(2, 1, sharex=True)
		self.canvas = FigureCanvasQTAgg(self.fig)
		right = QVBoxLayout()
		right.addWidget(NavigationToolbar2QT(self.canvas, self))
		right.addWidget(self.canvas)
		right_w = QWidget()
		right_w.setLayout(right)

		root = QHBoxLayout()
		root.addWidget(left)
		root.addWidget(right_w, 1)
		central = QWidget()
		central.setLayout(root)
		self.setCentralWidget(central)
		self.resize(1100, 650)
		self._set_tooltips()
		self.load_settings()
		self.plot()

	@staticmethod
	def _spin(lo, hi, val):
		s = QSpinBox()
		s.setRange(lo, hi)
		s.setValue(val)
		return s

	# --- actions ---
	def start_benchmark(self):
		n0, n1 = self.n_start.value(), self.n_end.value()
		if n1 < n0:
			QMessageBox.warning(self, "Invalid range", "N end must be >= N start.")
			return
		methods = [self.methods.item(i).text() for i in range(self.methods.count())
					if self.methods.item(i).checkState() == Qt.CheckState.Checked]
		if not methods:
			QMessageBox.warning(self, "No method", "Select at least one method.")
			return

		sizes = make_sizes(n0, n1, self.n_points.value(),
							log=self.n_spacing.currentText() == "log")

		self.save_settings()
		self.progress.setValue(0)
		self.run_btn.setEnabled(False)
		self.stop_btn.setEnabled(True)
		self.status.setText(f"Running ({len(sizes)} points)...")
		self.worker = BenchmarkWorker(methods, sizes, self.runs.value())
		self.worker.progress.connect(self.on_progress)
		self.worker.completed.connect(self.on_completed)
		self.worker.failed.connect(self.on_failed)
		self.worker.start()

	def stop_benchmark(self):
		if self.worker:
			self.worker.stop()

	def on_progress(self, done, total):
		self.progress.setMaximum(total)
		self.progress.setValue(done)

	def on_completed(self, results):
		self.results = results
		self._finish("Done.")
		self.plot()

	def on_failed(self, msg):
		self._finish("Error.")
		QMessageBox.critical(self, "Benchmark failed", msg)

	def _finish(self, text):
		self.run_btn.setEnabled(True)
		self.stop_btn.setEnabled(False)
		self.status.setText(text)

	# --- plotting ---
	def plot(self):
		self.ax_mean.cla()
		self.ax_std.cla()
		for name, (ns, means, stds) in self.results.items():
			rel = [100 * s / m if m else 0.0 for s, m in zip(stds, means)]
			self.ax_mean.plot(ns, means, marker="o", ms=3, label=name)
			self.ax_std.plot(ns, rel, marker="o", ms=3, label=name)

		self.ax_mean.set_ylabel("mean number of turns")
		self.ax_std.set_ylabel("std deviation (% of mean)")
		self.ax_std.set_xlabel("N")
		for ax in (self.ax_mean, self.ax_std):
			ax.set_xscale(self.x_scale.currentText())
			ax.grid(True, alpha=0.3)
		self.ax_mean.set_yscale(self.y_scale.currentText())
		self.ax_std.set_yscale("linear")
		if self.results:
			self.ax_mean.legend()
		self.canvas.draw_idle()

	# --- tooltips ---
	def _set_tooltips(self):
		tips = {
			self.n_start: "Smallest stack size N to test (included).",
			self.n_end: "Largest stack size N to test (included). Must be >= N start.",
			self.n_points: ("Number of N values to test between N start and N end.\n"
							"Rounding to integers can merge values, so the real "
							"number of points may be lower."),
			self.n_spacing: ("How the N values are distributed:\n"
								"linear: evenly spaced (10, 20, 30...)\n"
								"log: geometric (10, 100, 1000...)"),
			self.runs: ("Number of random inputs (permutations) generated for each N.\n"
						"More runs give a more reliable mean and deviation, "
						"but take longer."),
			self.x_scale: "Scale of the N axis on both plots. Can be changed at any time.",
			self.y_scale: ("Scale of the Y axis of the mean plot.\n"
							"The deviation plot always stays linear, because "
							"it can be exactly 0."),
			self.methods: ("Tick one or several sorting methods.\n"
							"Each one is drawn as its own curve."),
			self.run_btn: "Run the benchmark with the current settings.",
			self.stop_btn: "Stop the running benchmark and keep the partial results.",
			self.progress: "Number of (method, N) points computed so far.",
			self.status: "Current state of the benchmark.",
			self.canvas: ("Top: mean number of turns as a function of N.\n"
							"Bottom: standard deviation as a percentage of the mean."),
		}
		for widget, text in tips.items():
			widget.setToolTip(text)

		# Per-method tooltips in the list
		descriptions = {
			"radix": "Radix sort on ranks, one pass per bit. Fixed count for a given N.",
			"chunk": "Chunk / butterfly sort: push by rank chunks, then pull back the max.",
			"direct": "Selection sort: push the minimum to b each time. O(n^2) turns.",
			"turk": "Turk algorithm: always push the element with the cheapest rotation cost.",
		}
		for i in range(self.methods.count()):
			item = self.methods.item(i)
			if item.text() in descriptions:
				item.setToolTip(descriptions[item.text()])
					
	# --- persistent settings ---
	def _spins(self) -> dict:
		return {"n_start": self.n_start, "n_end": self.n_end,
				"n_points": self.n_points, "runs": self.runs}

	def _combos(self) -> dict:
		return {"n_spacing": self.n_spacing,
				"x_scale": self.x_scale, "y_scale": self.y_scale}

	def load_settings(self):
		s = QSettings("push_swap", "bench")
		for key, w in self._spins().items():
			w.setValue(s.value(key, w.value(), type=int))
		for key, w in self._combos().items():
			i = w.findText(s.value(key, w.currentText(), type=str))
			if i >= 0:
				w.setCurrentIndex(i)
		if s.contains("methods"):
			saved = set(filter(None, s.value("methods", "", type=str).split(",")))
			for i in range(self.methods.count()):
				item = self.methods.item(i)
				item.setCheckState(Qt.CheckState.Checked if item.text() in saved
								   else Qt.CheckState.Unchecked)
		size = s.value("size")
		if size is not None:
			self.resize(size)
		pos = s.value("pos")
		if pos is not None:
			self.move(pos)
		if s.value("maximized", False, type=bool):
			self.showMaximized()
	
	def save_settings(self):
		s = QSettings("push_swap", "bench")
		for key, w in self._spins().items():
			s.setValue(key, w.value())
		for key, w in self._combos().items():
			s.setValue(key, w.currentText())
		s.setValue("methods", ",".join(
			self.methods.item(i).text() for i in range(self.methods.count())
			if self.methods.item(i).checkState() == Qt.CheckState.Checked))
		if not self.isMaximized():
			s.setValue("size", self.size())
			s.setValue("pos", self.pos())

	def closeEvent(self, event):
		if self.worker and self.worker.isRunning():
			self.worker.stop()
			self.worker.wait()
		self.save_settings()
		super().closeEvent(event)