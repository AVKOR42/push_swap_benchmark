# src/benchmark.py
import random
import statistics

from src.algorithms import Algorithm
from src.stack import Stack


def make_sizes(n_start: int, n_end: int, points: int, log: bool = False) -> list[int]:
	"""N values from n_start to n_end (both included), linear or geometric spacing."""
	if points <= 1 or n_start == n_end:
		return [n_start]
	last = points - 1
	if log:
		ratio = n_end / n_start
		raw = [n_start * ratio ** (i / last) for i in range(points)]
	else:
		raw = [n_start + (n_end - n_start) * i / last for i in range(points)]
	# rounding to integers can create duplicates (e.g. log spacing at small N)
	return sorted({round(x) for x in raw})


def make_stacks(n: int, rng: random.Random) -> tuple[Stack, Stack]:
	"""Random input of n distinct numbers.

	A random permutation of 0..n-1 is its own ranking, so we fill `ind`
	directly instead of calling make_ind() (O(n^2)), which would dominate
	the benchmark time for large n.
	"""
	perm = list(range(n))
	rng.shuffle(perm)
	a = Stack("a", n)
	b = Stack("b", n)
	a.data = perm.copy()
	a.ind = perm
	a.last = n - 1
	return a, b


def benchmark_point(algo: Algorithm, n: int, runs: int,
					rng: random.Random | None = None) -> tuple[float, float]:
	"""Mean and standard deviation of the number of ops over `runs` random inputs."""
	rng = rng or random.Random()
	counts = []
	for _ in range(runs):
		a, b = make_stacks(n, rng)
		ops = algo(a, b)
		if not a.is_sorted():
			raise RuntimeError(f"algorithm failed to sort n={n}")
		counts.append(len(ops))
	std = statistics.stdev(counts) if runs > 1 else 0.0
	return statistics.fmean(counts), std